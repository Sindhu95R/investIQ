from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Import the main function from your consumer script
from dags.kafka_streams import main

# Define the DAG
dag = DAG(
    dag_id='crypto_data_consumer',
    default_args={
        'owner': 'airflow',
        'retries': 10000,  # Set a high retry limit
        'retry_delay': timedelta(seconds=10),  # Set a short retry delay
    },
    start_date=datetime(2023, 4, 15),
    catchup=False,
    schedule_interval=timedelta(days=1),  # Set a long schedule interval to avoid starting multiple instances
)

# Define the PythonOperator task
data_consumer_task = PythonOperator(
    task_id='data_consumer',
    python_callable=main,
    dag=dag,
)

# Set the task dependencies
data_consumer_task