from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator
from datetime import datetime, timedelta
import json, random, time, logging
from faker import Faker

logger = logging.getLogger(__name__)
fake = Faker()

MAX_MALICIOUS_IPS = 3
malicious_ips = {fake.ipv4(): 0}  # Initialize with one malicious IP

def load_connections():
    from airflow.models import Connection
    from airflow.utils import db

    db.merge_conn(
        Connection(
            conn_id="conn-0",
            conn_type="kafka",
            extra=json.dumps({"socket.timeout.ms": 10, "bootstrap.servers": "kafka-broker:29092"}),
        )
    )
    logger.info("Kafka connection loaded successfully.")

def generate_network_event():
    common_ports = {
        'SSH': 22,
        'HTTP': 80,
        'HTTPS': 443,
        'RDP': 3389,
        'FTP': 21,
        'SMTP': 25,
        'DNS': 53,
        'MYSQL': 3306,
        'POSTGRESQL': 5432,
        'MONGODB': 27017
    }

    # Generate 10 events per execution
    for _ in range(10):
        # Generate malicious login attempts
        if random.random() < 0.5:  # 50% chance of malicious activity
            if not malicious_ips or (random.random() < 0.3 and len(malicious_ips) < MAX_MALICIOUS_IPS):
                malicious_ips[fake.ipv4()] = 0
                if len(malicious_ips) > MAX_MALICIOUS_IPS:
                    malicious_ips.pop(next(iter(malicious_ips)))  # Remove oldest IP
            
            malicious_ip = random.choice(list(malicious_ips.keys()))
            protocol = random.choice(["SSH", "FTP", "RDP"])
            event = {
                "timestamp": time.time(),
                "source_ip": malicious_ip,
                "dest_ip": fake.ipv4(),
                "user": fake.user_name(),
                "event_type": "LOGIN_FAILED",
                "protocol": protocol,
                "port": common_ports[protocol]
            }
            yield ("network.logs", json.dumps(event))
            logger.info(f"Generated malicious event: {event}")
        
        # Generate normal traffic
        protocol = random.choice(["SSH", "HTTP", "HTTPS", "RDP", "FTP", "SMTP"])
        event = {
            "timestamp": time.time(),
            "source_ip": fake.ipv4(),
            "dest_ip": fake.ipv4(),
            "user": fake.user_name(),
            "event_type": random.choices(["LOGIN_SUCCESS", "PORT_SCAN", "CONNECTION"], weights=[0.7, 0.2, 0.1])[0],
            "protocol": protocol,
            "port": common_ports[protocol]
        }
        yield ("network.logs", json.dumps(event))
        logger.info(f"Generated normal event: {event}")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

with DAG("generate_network_logs", 
         schedule_interval=timedelta(seconds=10),
         default_args=default_args, 
         catchup=False) as dag:
    load_connections_task = PythonOperator(
        task_id='load_connections',
        python_callable=load_connections
    )

    produce_logs_task = ProduceToTopicOperator(
        task_id='produce_network_logs',
        topic="network.logs",
        kafka_config_id='conn-0',
        producer_function=generate_network_event,
        producer_function_args=[]
    )

    load_connections_task >> produce_logs_task