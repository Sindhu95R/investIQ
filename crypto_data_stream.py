import time
import requests
import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


def data_stream(sleep_interval=2):
 
    # Configure Kafka producer, replace localhost with your Kafka host IP address
    producer = KafkaProducer( bootstrap_servers='localhost:9092')
    
    api_key =  os.environ.get("COINMARKETCAP_API_KEY")
    url = os.environ.get("url")
    symbol_variable = os.environ.get("SYMBOL")
    convert_variable = os.environ.get("CONVERT")
    parameters = {
        'symbol': symbol_variable,
        'convert': convert_variable
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    while True:
        # Make API request for BTC and ETH prices
        response = requests.get(url, headers=headers, params=parameters)
        data = json.loads(response.text)
        
        
        # Process and send BTC data to Kafka
        process_and_send_data(producer, data, 'BTC', 'btc_prices')

        # Process and send ETH data to Kafka
        process_and_send_data(producer, data, 'ETH', 'eth_prices')

        # Sleep for the specified interval before making the next request
        time.sleep(sleep_interval)
        

def process_and_send_data(producer, data, symbol, topic):
    price_data = data['data'][symbol]['quote']['USD']

    extracted_data = {
        'timestamp': data['status']['timestamp'],
        'name': data['data'][symbol]['name'],
        'price': price_data['price'],
        'volume_24h': price_data['volume_24h'],
        'percent_change_24h': price_data['percent_change_24h']
    }  
    
    producer.send(topic, json.dumps(extracted_data).encode('utf-8'))

if __name__ == "__main__":
    data_stream(sleep_interval=2)