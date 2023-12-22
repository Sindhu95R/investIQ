import argparse
import os
import subprocess
import sys

import psutil
import threading
import time
from ipaddress import IPv4Network

from dht import utils
from dht.dht import DHT

# constants

PORT = 9789

# setup arguments
parser = argparse.ArgumentParser()
parser.add_argument("--bootstrap", help="an established node to bootstrap from."
                                        " to specify a mother node, pass \"mother\"")
args = parser.parse_args()

print("Welcome to the little-bird demo")

# get details about the local network
ip, ip_format = utils.Utils.get_local_ip()

print("Your IP: {0} Range: {1}".format(ip, ip_format))

if not args.bootstrap:
    print("No bootstrap node specified, scanning")
    possible_hosts = []

    for host in IPv4Network(ip_format):
        possible_hosts.append(str(host))

    print("Scanning {} possible host(s)".format(len(possible_hosts)))

    hits = []

    for i, host in enumerate(possible_hosts):
        x = (i / len(possible_hosts)) * 100
        if utils.Utils.check_host_up(host, PORT):
            hits.append(host)
        print("\r{0}%".format(x), end=str())

    print("Done!")

    if len(hits) == 0:
        exit("No bootstrap nodes found, start an instance node as a mother or specify a bootstrap node")
    else:
        print("hits found:", hits)
        host1, port1 = ip, PORT
        seeds = []
        for hit in hits:
            seeds.append((hit, PORT))
        dht1 = DHT(host1, port1, seeds=seeds)
        try:
            peer_list = dht1["peer_list"]
            if "{0}:{1}".format(host1, port1) not in peer_list:
                peer_list.append("{0}:{1}".format(host1, port1))
            dht1["peer_list"] = peer_list
        except:
            exit("Something went wrong during bootstrapping, please kindly try again")
elif args.bootstrap == "mother":
    print("Starting current instance as mother node")
    host1, port1 = ip, PORT
    dht1 = DHT(host1, port1)  # mother node
    dht1["peer_list"] = ["{0}:{1}".format(host1, port1)]
else:
    bootstrap = args.bootstrap
    bootstrap = bootstrap.split(":")
    if len(bootstrap) == 2:
        print("bootstrapping with {0}:{1}".format(bootstrap[0], bootstrap[1]))
        if not utils.Utils.check_host_up(bootstrap[0], int(bootstrap[1])):
            exit("there is no bootstrap instance listening on {0}:{1}".format(bootstrap[0], bootstrap[1]))
        host1, port1 = ip, PORT
        dht1 = DHT(host1, port1, seeds=[(bootstrap[0], int(bootstrap[1]))])
        try:
            peer_list = dht1["peer_list"]
            if "{0}:{1}".format(host1, port1) not in peer_list:
                peer_list.append("{0}:{1}".format(host1, port1))
            dht1["peer_list"] = peer_list
        except:
            exit("Something went wrong during bootstrapping, please kindly try again")
    else:
        exit("Invalid bootstrap node format. Use <host>:<port>")


# launch tcp server, so bootstrapper can find us
def simple_server():
    subprocess.Popen("netcat -l {0} -p {1} -k".format(ip, PORT), close_fds=True, shell=True)


try:
    server_thread = threading.Thread(target=simple_server())
    server_thread.daemon = True
    server_thread.start()
except Exception as e:
    print(e)
    exit("Could not bind bootstrap listening server")


def update_peer_list():
    """
    Updates peer list by pinging peers every 15 seconds. If no response is received, the peer is pruned from the
    peer list
    :return: None
    """
    octets = ip.split(".")
    router = "{0}.{1}.{2}.1".format(octets[0], octets[1], octets[2])
    if utils.Utils.check_host_up(router, 80):
        for i, peer in enumerate(dht1["peer_list"]):
            host, port = peer.split(":")
            peer_list = dht1["peer_list"]
            if not utils.Utils.check_host_up(host, int(port)):
                peer_list.pop(i)
            dht1["peer_list"] = peer_list
    else:
        cleanup()
        print("\nrouter down! you are not connected to the Internet")
        os._exit(1)
    timer = threading.Timer(15.0, update_peer_list)
    timer.daemon = True
    timer.start()


# call peer list updater

time.sleep(3)

update_peer_list()


def cleanup():
    """
    Cleans up after shutdown, kills netcat processes
    :return: Nothing
    """
    PROCNAME = "netcat"

    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            print("\nKilling [{1}]{0}".format(PROCNAME, proc.pid))
            proc.kill()

while True:
    try:
        command = input("Enter a command:")
        command = command.split(" ")
        if command[0] == "/exit":
            peer_list = dht1["peer_list"]
            if "{0}:{1}".format(ip, PORT) in peer_list:
                peer_list.remove("{0}:{1}".format(ip, PORT))
                dht1["peer_list"] = peer_list
            cleanup()
            exit("Shutdown was successful")
        elif command[0] == "/push":
            if len(command) != 3:
                print("Incorrect usage: /push <key> <value>")
            else:
                print("/push {0} {1}".format(command[1], command[2]))
                dht1[command[1]] = command[2]
        elif command[0] == "/pull":
            if len(command) == 2:
                print("/pull {0}".format(command[1]))
                try:
                    print(dht1[command[1]])
                    print("Pulled: {0}={1}".format(command[1], dht1[command[1]]))
                except KeyError:
                    print("Key {0} not found.".format(command[1]))
            else:
                print("Incorrect usage: /pull <key>")
        elif command[0] == "/peers":
            for i, peer in enumerate(dht1["peer_list"]):
                print("{0}: {1}".format(i, peer))
        else:
            print("Invalid command. Consult the documentation: <https://github.com/ZigmundVonZaun/little-bird>")
    except (KeyboardInterrupt, SystemExit):
        print("shutting down gracefully")
        cleanup()
        peer_list = dht1["peer_list"]
        if "{0}:{1}".format(ip, PORT) in peer_list:
            peer_list.remove("{0}:{1}".format(ip, PORT))
            dht1["peer_list"] = peer_list
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
