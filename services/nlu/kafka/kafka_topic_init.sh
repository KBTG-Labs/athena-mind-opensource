#!/bin/sh  
KAFKA_TOPIC_COMMAND=/opt/bitnami/kafka/bin/kafka-topics.sh
KAFKA_TOPIC_FILE=/tmp/kafka/kafka_topic.json
BOOTSTRAP_SERVER=kafka:9092

${KAFKA_TOPIC_COMMAND} --bootstrap-server ${BOOTSTRAP_SERVER} --list
echo "start creating topic"
jq -c '.topics[]' ${KAFKA_TOPIC_FILE} | while read i;do
    name=$(echo $i | jq -r .name)
    partition=$(echo $i | jq -r .partition)
    replica=$(echo $i | jq -r .replica)
        configs=$(echo $i | jq -r .config[]?)
    command="${KAFKA_TOPIC_COMMAND} --create --bootstrap-server ${BOOTSTRAP_SERVER} --replication-factor $replica --partitions $partition --topic $name"
    for config in $configs;do
            if [ $config != "[" ] && [ $config != "]" ] && [ $config != "null" ];then
                option=" --config "
                configOpt=$option$config
                command=$command$configOpt
                fi
            done
    eval $command
done
echo "all topics have been created"
echo "==== topic list ===="
${KAFKA_TOPIC_COMMAND} --bootstrap-server ${BOOTSTRAP_SERVER} --list