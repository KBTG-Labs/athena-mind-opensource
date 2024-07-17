from dataclasses import dataclass
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass
class AppTelemetry:
    enable_telemetry: bool = False
    tracer: Optional[trace.Tracer] = None

app_telemetry = AppTelemetry()

def configure_tracing(name: str, enable_telemetry: bool, collector_endpoint: Optional[str] = None):
    app_telemetry.enable_telemetry = enable_telemetry
    if enable_telemetry:
        if collector_endpoint is None:
            raise KeyError("env 'TELEMETRY_COLLECTOR_ENDPOINT' is not set")
        
        jaeger_exporter = JaegerExporter(
            collector_endpoint=collector_endpoint,
        )
        resource = Resource(attributes={
            SERVICE_NAME: name,
        })
        trace_span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace.get_tracer_provider().add_span_processor(trace_span_processor)
                
        app_telemetry.tracer = trace.get_tracer(name)
