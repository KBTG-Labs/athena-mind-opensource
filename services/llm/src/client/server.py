from common.log import Logger
from common.constant.domain import SERVER_LLM as DOMAIN
from common.telemetry import configure_tracing

from .config import Configs
from .constructor import init_services


class AppServer:
    def __init__(self):
        configs = Configs()
        configure_tracing(
            name=configs.service_name,
            enable_telemetry=configs.enable_telemetry,
            collector_endpoint=configs.telemetry_collector_endpoint,
        )
        services = init_services(configs=configs)
        self.logger = Logger.get_logger(DOMAIN)
        self.consumer_service = services.consumer_service
        self.consumer_topics = [configs.mq_consumer_topic]
        self.consumer_commit_count = configs.mq_consumer_min_commit_count

    def start_mq(self):
        try:
            success_message_count = 0
            self.consumer_service.subscribe(topics=self.consumer_topics)

            self.logger.info("Server Configuring Done. Server is Ready")

            while True:
                messages = self.consumer_service.consume()
                if not messages:
                    continue

                is_success = self.consumer_service.process(messages)
                if is_success:
                    success_message_count += 1

                    if success_message_count % self.consumer_commit_count == 0:
                        self.consumer_service.commit(asynchronous=True)

        finally:
            self.consumer_service.close()

    def start(self):
        self.start_mq()
