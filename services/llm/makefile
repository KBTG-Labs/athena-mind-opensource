# Install all required dependencies
# Example: make app-install
app-install: 
	pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt


# Start service 
# Example: make app-start
app-start:
	ENV_FILE=.env python ./src/main.py


# Test the app
app-test:
	cd src && PYTHONPATH=$(shell pwd)/src pytest --cov=.


# Create topic in queue
# Example: make dkafka-create-topic TOPIC="my-first-topic" REPLICATION_FACTOR=1 PARTITIONS=1
# Value: 
# 	- TOPIC: Topic name that we want to create
#	- REPLICATION_FACTOR (optional): The number of copies (replicas) of a topic's partitions [default = 1]
#	- PARTITIONS (optional): The number of paritions of a topic [default = 1]
REPLICATION_FACTOR = 1
PARTITIONS = 1
dkafka-create-topic:
	docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server kafka:9093 --replication-factor $(REPLICATION_FACTOR) --partitions $(PARTITIONS) --topic $(TOPIC)


# Delete topic in queue
# Example: make dkafka-delete-topic TOPIC="my-first-topic"
# Value: 
# 	- TOPIC: Topic name that we want to delete
dkafka-delete-topic:
	docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9093 --delete --topic $(TOPIC)


# Publish to queue with topic and message
# Example: make dkafka-publish-queue TOPIC="my-first-topic" MESSAGE="My First Message"
# Value: 
# 	- TOPIC: Topic name where we want to publish
#	- MESSAGE: Message
dkafka-publish-queue:
	@echo '$(MESSAGE)' | docker exec -i kafka /opt/kafka/bin/kafka-console-producer.sh --broker-list kafka:9093 --topic $(TOPIC)


# Publish to queue with topic and message (use payload as file)
# Example: make dkafka-publish-queue-json TOPIC="my-first-topic" MQ_PAYLOAD="file-name"
# Value: 
# 	- TOPIC: Topic name where we want to publish
#	- MQ_PAYLOAD: Payload file
dkafka-publish-queue-json:
	cat ./example/mq/$(MQ_PAYLOAD).json | docker exec -i kafka /opt/kafka/bin/kafka-console-producer.sh --broker-list kafka:9093 --topic $(TOPIC)


# Setup kafka topics
dkafka-create-all-topics:
	make dkafka-create-topic TOPIC="llm-request" && \
	make dkafka-create-topic TOPIC="llm-response" && \
	make dkafka-create-topic TOPIC="error-queue"