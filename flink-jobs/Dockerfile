FROM maven:3.8.4-openjdk-11

# Install basic utilities
RUN apt-get update
RUN apt-get install -y curl wget jq
RUN rm -rf /var/lib/apt/lists/*

# Download and install Flink
ENV FLINK_VERSION=1.17.1
ENV SCALA_VERSION=2.12

RUN wget -q "https://archive.apache.org/dist/flink/flink-${FLINK_VERSION}/flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz"
RUN tar -xzf "flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz"
RUN mv "flink-${FLINK_VERSION}" /opt/flink
RUN rm "flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz"

ENV PATH=$PATH:/opt/flink/bin
