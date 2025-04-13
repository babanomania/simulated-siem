from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.window import TumblingProcessingTimeWindows
import json

def parse_event(raw):
    data = json.loads(raw)
    return (data["source_ip"], data["event_type"], 1)

def detect_brute_force(source_ip, count):
    return json.dumps({
        "alert": "Brute Force",
        "source_ip": source_ip,
        "fail_count": count
    })

env = StreamExecutionEnvironment.get_execution_environment()
env.set_runtime_mode(RuntimeExecutionMode.STREAMING)

kafka_source = FlinkKafkaConsumer(
    topics='network.logs',
    deserialization_schema=Types.STRING(),
    properties={'bootstrap.servers': 'kafka:9092', 'group.id': 'flink-group'}
)

kafka_sink = FlinkKafkaProducer(
    topic='alerts.security',
    serialization_schema=Types.STRING(),
    producer_config={'bootstrap.servers': 'kafka:9092'}
)

stream = env.add_source(kafka_source)

parsed = stream     .map(parse_event, output_type=Types.TUPLE([Types.STRING(), Types.STRING(), Types.INT()]))     .filter(lambda x: x[1] == "LOGIN_FAILED")     .key_by(lambda x: x[0])     .window(TumblingProcessingTimeWindows.of(10000))     .reduce(lambda a, b: (a[0], a[1], a[2] + b[2]))     .filter(lambda x: x[2] >= 5)     .map(lambda x: detect_brute_force(x[0], x[2]), output_type=Types.STRING())

parsed.add_sink(kafka_sink)

env.execute("SIEM Brute Force Detector")