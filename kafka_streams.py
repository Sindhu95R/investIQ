from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from pymongo import MongoClient
import json
import signal
import sys

# MongoDB connection setup
connection_string = 'mongodb+srv://sindhu:Meno0OXqrHBf7FIc@investiq.svrgpk4.mongodb.net/'
mongo_client = MongoClient(connection_string)

mongo_db = mongo_client['crypto_data']
raw_prices_collection = mongo_db['raw_prices']
significant_changes_collection = mongo_db['significant_changes']

def process_message(msg, producer):
    # Deserialize the message value
    deserialized_msg = json.loads(msg.value())

    # Insert the raw price data into the raw_prices collection in MongoDB
    raw_prices_collection.insert_one({
        'timestamp': deserialized_msg['timestamp'],
        'symbol': deserialized_msg['name'],
        'price': deserialized_msg['price'],
        'volume_24h': deserialized_msg['volume_24h'],
        'percent_change_24h': deserialized_msg['percent_change_24h']
    })
    #print("Inserted raw price data into MongoDB")

    # Check if the percent change is greater than a certain threshold (e.g., 1%)
    if abs(deserialized_msg['percent_change_24h']) > 1:
        #print("Significant price change detected:")

        # Insert the significant price change data into the significant_changes collection in MongoDB
        significant_changes_collection.insert_one({
            'timestamp': deserialized_msg['timestamp'],
            'symbol': deserialized_msg['name'],
            'price': deserialized_msg['price'],
            'volume_24h': deserialized_msg['volume_24h'],
            'percent_change_24h': deserialized_msg['percent_change_24h']
        })
        #print("Inserted significant price change data into MongoDB")

        # Produce the significant price change message to the appropriate Kafka topic
        new_topic = 'btc_price24' if deserialized_msg['name'] == 'Bitcoin' else 'eth_price24'
        producer.produce(new_topic, key=deserialized_msg['name'], value=json.dumps(deserialized_msg))
        producer.flush()
        #print("Produced significant price change message to topic:", new_topic)


def main():
    # Set up the Kafka consumer configuration

    #print("line 1")
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'crypto_stream_processor',
        'auto.offset.reset': 'earliest',
    }

    # Create a Kafka consumer instance
    consumer = Consumer(conf)

    # Subscribe to the 'btc_prices' and 'eth_prices' topics
    consumer.subscribe(['btc_prices', 'eth_prices'])

    # Set up the Kafka producer configuration
    producer_conf = {
        'bootstrap.servers': 'localhost:9092',
    }

    # Create a Kafka producer instance
    producer = Producer(producer_conf)

    # Register the signal handler with the lambda function to pass consumer
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, consumer))

    # Poll for messages and process them
    while True:
        msg = consumer.poll(1.0)
        #print(msg)
        if msg is None:
            # No message received in the last poll interval
            continue
        elif msg.error():
            # Handle any errors that occurred while polling for messages
            raise KafkaException(msg.error())
        else:
            process_message(msg, producer)


def signal_handler(sig, frame, consumer):
    #print('Shutting down gracefully...')
    consumer.close()
    sys.exit(0)


if __name__ == "__main__":
    main()