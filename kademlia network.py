
import asyncio
from dht.dht import DHT
import json

def split_message(message, num_pieces):
    # Split a JSON message into multiple pieces
    message_json = json.dumps(message)
    piece_size = len(message_json) // num_pieces
    pieces = [message_json[i:i + piece_size] for i in range(0, len(message_json), piece_size)]
    return pieces

def assemble_message(pieces):
    # Assemble pieces into the original JSON message
    # Filter out None values before joining
    valid_pieces = [piece for piece in pieces if piece is not None]

    # Join valid pieces with commas and surround with square brackets to create a valid JSON array
    json_array = f"[{''.join(valid_pieces)}]"

    # If there are no valid pieces, return None to indicate an issue
    if not valid_pieces:
        return None

    return json_array

async def retrieve_piece(node, key):
    # Asynchronously retrieve a piece from a node
    return await asyncio.to_thread(node.__getitem__, key)


async def main():
    # Create mother node
    host1, port1 = 'localhost', 9789
    dht1 = DHT(host1, port1)
    mother_node_id = str(dht1.peer)

    # Create additional nodes
    nodes = []
    for i in range(3):
        host, port = "localhost", 9788 - i
        node = DHT(host, port, seeds=[(host1, port1)])
        nodes.append(node)

    # Original JSON message
    original_message = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }

    # Split the JSON message into pieces
    message_pieces = split_message(original_message, len(nodes))

    # Store each piece in a different node
    for i, node in enumerate(nodes):
        key = f"piece_{i}"
        node[key] = message_pieces[i]

    # Asynchronously retrieve pieces from different nodes
    tasks = [retrieve_piece(node, f"piece_{i}") for i, node in enumerate(nodes)]
    retrieved_pieces = await asyncio.gather(*tasks)

    # Assemble the pieces into the original JSON message
    retrieved_message = assemble_message(retrieved_pieces)

    # Print the results
    print("Original JSON Message:", original_message)
    print("Retrieved JSON Message:", retrieved_message)

if __name__ == "__main__":
    asyncio.run(main())

"""
import asyncio
from dht.dht import DHT
import json

async def retrieve_piece(node, key):
    # Asynchronously retrieve a piece from a node
    return await asyncio.to_thread(node.get, key, lambda data: data)

def split_message(message, num_pieces):
    # Split a JSON message into multiple pieces
    message_json = json.dumps(message)
    piece_size = len(message_json) // num_pieces
    pieces = [message_json[i:i + piece_size] for i in range(0, len(message_json), piece_size)]
    return pieces

def assemble_message(pieces):
    # Assemble pieces into the original JSON message
    # Filter out None values before joining
    valid_pieces = [piece for piece in pieces if piece is not None]

    # Join valid pieces with commas and surround with square brackets to create a valid JSON array
    json_array = f"[{','.join(valid_pieces)}]"

    # If there are no valid pieces, return None to indicate an issue
    if not valid_pieces:
        return None

    return json.loads(json_array)

async def main():
    # Create mother node
    host1, port1 = 'localhost', 9789
    dht1 = DHT(host1, port1)
    mother_node_id = str(dht1.peer)

    # Create additional nodes
    nodes = []
    for i in range(10):
        host, port = "localhost", 9788 - i
        node = DHT(host, port, seeds=[(host1, port1)])
        nodes.append(node)

    # Original JSON message
    original_message = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }

    # Split the JSON message into pieces
    message_pieces = split_message(original_message, len(nodes))

    # Sort nodes based on proximity to the target key
    nodes.sort(key=lambda node: abs(hash(node.peer) - hash(message_pieces[0])))

    # Asynchronously retrieve pieces from different nodes
    tasks = [retrieve_piece(node, f"piece_{i}") for i, node in enumerate(nodes)]
    retrieved_pieces = await asyncio.gather(*tasks)

    # Assemble the pieces into the original JSON message
    retrieved_message = assemble_message(retrieved_pieces)

    # Print the results
    print("Original JSON Message:", original_message)
    print("Retrieved JSON Message:", retrieved_message)

if __name__ == "__main__"   :
    asyncio.run(main())
"""





