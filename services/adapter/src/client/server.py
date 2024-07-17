import uvicorn
from fastapi import FastAPI
from langserve import add_routes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from client.config import Configs
from client.constructor import get_adapters
from common import AgentState
from common.log import CorrelationIdMiddleware, get_logging_config
from common.telemetry import configure_tracing

app = FastAPI(
    title="Adapter Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

app.add_middleware(CorrelationIdMiddleware)
class AppServer:
    def __init__(self):
        configs = Configs()
        configure_tracing(
            name=configs.service_name,
            enable_telemetry=configs.enable_telemetry,
            collector_endpoint=configs.telemetry_collector_endpoint,
        )
        FastAPIInstrumentor.instrument_app(app)
        
        self.host = configs.app_host
        self.port = configs.app_port
        self.logging_config = get_logging_config(configs.log_level, configs.log_timezone)

        self.adapters = get_adapters(configs)

    def start(self):
        for adapter, chain in self.adapters.items(): 
            add_routes(
                app,
                chain.with_types(input_type=AgentState, output_type=str),
                path=f"/api/v1/chain/{adapter}"
            )
        
        uvicorn.run(
            app,
            host=self.host,
            port=self.port,
            log_config=self.logging_config,
        )

        
