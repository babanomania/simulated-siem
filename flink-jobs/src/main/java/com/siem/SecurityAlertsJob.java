package com.siem;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.siem.model.NetworkEvent;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

public class SecurityAlertsJob {
    public static void main(String[] args) throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        String networkTopic = System.getenv("KAFKA_TOPIC_NETWORK");
        String alertsTopic = System.getenv("KAFKA_TOPIC_ALERTS");

        KafkaSource<String> source = KafkaSource.<String>builder()
                .setBootstrapServers("kafka-broker:29092")
                .setTopics(networkTopic)
                .setGroupId("flink-group")
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();

        KafkaSink<String> sink = KafkaSink.<String>builder()
                .setBootstrapServers("kafka-broker:29092")
                .setRecordSerializer(KafkaRecordSerializationSchema.builder()
                        .setTopic(alertsTopic)
                        .setValueSerializationSchema(new SimpleStringSchema())
                        .build())
                .build();

        DataStream<String> stream = env.fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka Source");

        ObjectMapper mapper = new ObjectMapper();

        stream
            .map(value -> {
                JsonNode node = mapper.readTree(value);
                return new NetworkEvent(
                    node.get("source_ip").asText(),
                    node.get("event_type").asText(),
                    1
                );
            })
            .filter(event -> event.getEventType().equals("LOGIN_FAILED"))
            .keyBy(NetworkEvent::getSourceIp)
            .window(TumblingProcessingTimeWindows.of(Time.seconds(60)))
            .reduce((a, b) -> new NetworkEvent(
                a.getSourceIp(),
                a.getEventType(),
                a.getCount() + b.getCount()
            ))
            .filter(event -> event.getCount() >= 3)
            .map(event -> {
                ObjectNode schema = mapper.createObjectNode();
                schema.putObject("schema")
                    .put("type", "struct")
                    .putArray("fields")
                    .add(mapper.createObjectNode()
                        .put("type", "string")
                        .put("field", "alert_id"))
                    .add(mapper.createObjectNode()
                        .put("type", "string")
                        .put("field", "alert"))
                    .add(mapper.createObjectNode()
                        .put("type", "string")
                        .put("field", "source_ip"))
                    .add(mapper.createObjectNode()
                        .put("type", "int32")
                        .put("field", "fail_count"));

                ObjectNode payload = mapper.createObjectNode();
                payload.put("alert_id", java.util.UUID.randomUUID().toString());
                payload.put("alert", "Brute Force");
                payload.put("source_ip", event.getSourceIp());
                payload.put("fail_count", event.getCount());

                schema.set("payload", payload);
                return mapper.writeValueAsString(schema);
            })
            .sinkTo(sink);

        env.execute("SIEM Brute Force Detector");
    }
}
