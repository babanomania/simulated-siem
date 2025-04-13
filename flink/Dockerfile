FROM apache/flink:1.17

USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install apache-flink kafka-python

WORKDIR /opt/flink-job
COPY flink_job.py .

ENTRYPOINT ["python3", "flink_job.py"]
