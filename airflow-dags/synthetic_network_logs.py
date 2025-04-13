from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json, random, time
from faker import Faker

fake = Faker()

def produce_logs():
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    for _ in range(100):
        event = {
            "timestamp": time.time(),
            "source_ip": fake.ipv4(),
            "dest_ip": fake.ipv4(),
            "user": fake.user_name(),
            "event_type": random.choices(["LOGIN_FAILED", "LOGIN_SUCCESS", "PORT_SCAN", "CONNECTION"], weights=[0.5, 0.3, 0.1, 0.1])[0],
            "protocol": random.choice(["SSH", "HTTP", "HTTPS", "RDP"]),
            "port": random.randint(1, 65535)
        }
        producer.send("network.logs", json.dumps(event).encode())
    producer.flush()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

with DAG("generate_network_logs", schedule_interval='@hourly', default_args=default_args, catchup=False) as dag:
    task = PythonOperator(task_id='produce_network_logs', python_callable=produce_logs)