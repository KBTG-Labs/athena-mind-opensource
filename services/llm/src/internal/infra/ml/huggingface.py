import torch

from typing import Optional, Tuple, List
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.utils.logging import add_handler, disable_default_handler
from huggingface_hub import login

from common.constant.domain import INFRA_HUGGINGFACE as DOMAIN
from common.log import Logger
from common.decorator import retry
from common.util.torch import select_torch_dtype, select_torch_device
from internal.domain.ml import ILLMModel
from internal.domain.entity import LLMRequest, LLMResponse

from common.decorator import trace

START_PROMPT_TAG, END_PROMPT_TAG = "[INST]", "[/INST]"


class HuggingFace(ILLMModel):
    def __init__(
        self,
        model_path: str,
        model_do_sample: bool,
        model_max_new_tokens: int,
        model_torch_dtype: str,
        model_batch_required: bool,
        model_torch_device: int,
        huggingface_api_key: Optional[str],
    ):
        self.logger = Logger.get_logger(DOMAIN)

        # Config Transformers Logger
        disable_default_handler()
        add_handler(Logger.get_handler())

        self.device = select_torch_device(device=model_torch_device)
        self.torch_dtype = select_torch_dtype(model_torch_dtype)

        self.model_max_new_tokens = model_max_new_tokens
        self.model_do_sample = model_do_sample
        self.model_batch_required = model_batch_required

        try:
            if not model_path:
                raise Exception("HUGGINGFACE_MODEL_PATH must be defined")
            if huggingface_api_key:
                login(token=huggingface_api_key)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=self.torch_dtype,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        except Exception as e:
            self.logger.error(f"Error Loading Model {model_path}: {e}")
            raise

    @retry(max_retries=1, delay=1, logger=Logger.get_logger(DOMAIN))
    def __call_model(self, model_input: torch.Tensor, attention_mask: torch.Tensor) -> List[str]:
        self.logger.info(f"__call_model (payload:{model_input})")
        generated_ids = self.model.generate(
            model_input,
            attention_mask=attention_mask,
            pad_token_id=self.tokenizer.pad_token_id,
            max_new_tokens=self.model_max_new_tokens,
            do_sample=self.model_do_sample,
        )
        model_responses = self.tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )
        return model_responses

    @trace
    def __pad_batch_inputs(self, batch_inputs: List[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        self.logger.info(f"__pad_batch_inputs (payload:{batch_inputs})")
        padded_inputs, attention_masks = [], []
        max_length = max(input_tensor.size(1) for input_tensor in batch_inputs)
        for input_tensor in batch_inputs:
            padding_length = max_length - input_tensor.size(1)
            padded_input = torch.nn.functional.pad(
                input_tensor,
                (0, padding_length),
                value=self.tokenizer.pad_token_id,
            )
            attention_mask = torch.nn.functional.pad(
                torch.ones_like(input_tensor),
                (0, padding_length),
                value=0,
            )
            padded_inputs.append(padded_input)
            attention_masks.append(attention_mask)

        return torch.cat(padded_inputs, dim=0).to(self.device), torch.cat(attention_masks, dim=0).to(self.device)

    @trace
    def generate_response(self, message: LLMRequest) -> LLMResponse:
        self.logger.info(f"generate_response (payload:{message})")
        prompt = f"{START_PROMPT_TAG} {message.prompt} {END_PROMPT_TAG}"
        encoded = self.tokenizer.encode(text=prompt, return_tensors="pt")
        model_input = encoded.to(self.device)
        attention_mask = torch.ones_like(model_input).to(self.device)
        model_output = self.__call_model(
            model_input=model_input,
            attention_mask=attention_mask,
        )
        decoded_responses, error = model_output.results, model_output.error
        is_contain_answer = decoded_responses and \
            isinstance(decoded_responses, list) and \
            len(decoded_responses) > 0
        response = decoded_responses[0].split(END_PROMPT_TAG)[-1].strip() \
            if is_contain_answer else None

        return LLMResponse(
            id=message.id,
            results=response,
            error=error,
            destination=message.destination,
        )

    @trace
    def generate_batch_responses(self, messages: List[LLMRequest]) -> List[LLMResponse]:
        self.logger.info(f"generate_batch_responses (payload:{messages})")
        ids, batch_inputs, destinations = [], [], []
        for message in messages:
            prompt = f"{START_PROMPT_TAG} {message.prompt} {END_PROMPT_TAG}"
            encoded = self.tokenizer.encode(prompt, return_tensors="pt")
            batch_inputs.append(encoded)
            ids.append(message.id)
            destinations.append(message.destination)

        model_input, attention_mask = self.__pad_batch_inputs(
            batch_inputs=batch_inputs)
        model_output = self.__call_model(
            model_input=model_input,
            attention_mask=attention_mask,
        )
        if model_output.error:
            return [
                LLMResponse(
                    id=message.id,
                    error=model_output.error,
                    destination=message.destination,
                )
                for message in messages
            ]

        return [
            LLMResponse(
                id=ids[idx],
                results=response.split(END_PROMPT_TAG)[-1].strip(),
                destination=destinations[idx],
            )
            for idx, response in enumerate(model_output.results)
        ]
