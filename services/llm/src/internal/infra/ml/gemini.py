import asyncio
from typing import List, Optional

import google.generativeai as genai
import nest_asyncio
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory

from common.constant.domain import INFRA_GEMINI as DOMAIN
from common.decorator import detach_async_worker, retry, trace
from common.decorator.trace import trace_with_message_id
from common.log import Logger
from internal.domain.entity import LLMRequest, LLMResponse
from internal.domain.ml import ILLMModel


class Gemini(ILLMModel):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        model_max_output_token: int,
        model_temperature: float,
        model_top_p: float,
        model_stream_required: bool,
        model_batch_required: bool,
        model_request_workers: Optional[int] = 1,
        model_transport: Optional[str] = None,
    ):
        self.logger = Logger.get_logger(DOMAIN)
        self.model_stream_required = model_stream_required
        self.model_batch_required = model_batch_required

        if self.model_batch_required:
            nest_asyncio.apply()
            self.request_workers = model_request_workers

        self.model_transport = model_transport \
            if model_transport in ["rest", "grpc", "grpc_asyncio"] else "grpc"

        try:
            genai.configure(api_key=api_key, transport=self.model_transport)
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "max_output_tokens": model_max_output_token,
                    "temperature": model_temperature,
                    "top_p": model_top_p,
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
        except Exception as e:
            self.logger.error(f"Error loading gemini: {e}")
            raise
    
    @retry(max_retries=3, delay=1, logger=Logger.get_logger(DOMAIN))
    @trace
    def __call_model(self, prompt: str) -> str:
        response = self.model.generate_content(
            contents=prompt,
            stream=self.model_stream_required,
        )

        if self.model_stream_required:
            return "".join(map(lambda x: str(x.text), response))

        return response.text

    @retry(max_retries=3, delay=1, logger=Logger.get_logger(DOMAIN))
    @trace
    async def __call_model_async(self, prompt: str) -> str:
        responses = await self.model.generate_content_async(
            contents=prompt,
            stream=self.model_stream_required,
        )

        if self.model_stream_required:
            output = ""
            async for response in responses:
                output += response.text
            return output

        return responses.text

    @detach_async_worker()
    @trace_with_message_id
    async def __process_async_call(self, message: LLMRequest) -> LLMResponse:
        model_response = await self.__call_model_async(prompt=message.prompt)
        return LLMResponse(
            id=message.id,
            results=model_response.results,
            error=model_response.error,
            destination=message.destination,
        )
    
    @trace
    async def __generate_batch_responses_async(self, messages: List[LLMRequest]) -> List[LLMResponse]:
        responses = []
        async for response in self.__process_async_call(messages):
            responses.append(response)
        return responses

    @trace_with_message_id
    def generate_response(self, message: LLMRequest) -> LLMResponse:
        self.logger.info(f"generate_response (payload:{message})")
        model_response = self.__call_model(prompt=message.prompt)
        return LLMResponse(
            id=message.id,
            results=model_response.results,
            error=model_response.error,
            destination=message.destination,
        )

    @trace
    def generate_batch_responses(self, messages: List[LLMRequest]) -> List[LLMResponse]:
        self.logger.info(f"generate_batch_responses (payload:{messages})")
        task = asyncio.create_task(
            self.__generate_batch_responses_async(messages))
        return asyncio.get_event_loop().run_until_complete(task)
