import asyncio
import time
from typing import NamedTuple, Optional, Dict, List
import openai
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logs import LOGGER
from config import CONFIG
from utils import (
    count_message_tokens,
    count_string_tokens,
    get_max_completion_tokens,
)
import os
from openai import AzureOpenAI

os.environ["TOKENIZERS_PARALLELISM"] = "false"

@dataclass
class BaseChatbot(ABC):
    """Abstract GPT class"""
    mode: str = "API"

    @abstractmethod
    def ask(self, msg: str) -> str:
        """Ask GPT a question and get an answer"""

    @abstractmethod
    def ask_batch(self, msgs: List) -> str:
        """Ask GPT multiple questions and get a series of answers"""

    @abstractmethod
    def ask_code(self, msgs: List) -> str:
        """Ask GPT multiple questions and get a piece of code"""


class BaseGPTAPI(BaseChatbot):
    """GPT API abstract class, requiring all inheritors to provide a series of standard capabilities"""
    system_prompt = 'You are a helpful assistant.'

    def _user_msg(self, msg: str) -> Dict[str, str]:
        return {"role": "user", "content": msg}

    def _assistant_msg(self, msg: str) -> Dict[str, str]:
        return {"role": "assistant", "content": msg}

    def _system_msg(self, msg: str) -> Dict[str, str]:
        return {"role": "system", "content": msg}

    def _system_msgs(self, msgs: List[str]) -> List[Dict[str, str]]:
        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self):
        return self._system_msg(self.system_prompt)

    def ask(self, msg: str) -> str:
        message = [self._default_system_msg(), self._user_msg(msg)]
        rsp = self.completion(message)
        return self.get_choice_text(rsp)

    def aask(self, msg: str, system_msgs: Optional[List[str]] = None) -> str:
        if system_msgs:
            message = self._system_msgs(system_msgs) + [self._user_msg(msg)]
        else:
            message = [self._default_system_msg(), self._user_msg(msg)]
        rsp, token_cost = self.acompletion_text(message, stream=False)
        return rsp, token_cost

    def _extract_assistant_rsp(self, context):
        return "\n".join([i["content"] for i in context if i["role"] == "assistant"])

    def ask_batch(self, msgs: List) -> str:
        context = []
        for msg in msgs:
            umsg = self._user_msg(msg)
            context.append(umsg)
            rsp = self.completion(context)
            rsp_text = self.get_choice_text(rsp)
            context.append(self._assistant_msg(rsp_text))
        return self._extract_assistant_rsp(context)

    def aask_batch(self, msgs: List) -> str:
        """Sequential questioning"""
        context = []
        for msg in msgs:
            umsg = self._user_msg(msg)
            context.append(umsg)
            rsp_text = self.acompletion_text(context)
            context.append(self._assistant_msg(rsp_text))
        return self._extract_assistant_rsp(context)

    def ask_code(self, msgs: List[str]) -> str:
        """FIXME: No code segment filtering has been done here, and all results are actually displayed"""
        rsp_text = self.ask_batch(msgs)
        return rsp_text

    def aask_code(self, msgs: List[str]) -> str:
        """FIXME: No code segment filtering has been done here, and all results are actually displayed"""
        rsp_text = self.aask_batch(msgs)
        return rsp_text

    @abstractmethod
    def completion(self, messages: List[Dict]):
        """All GPTAPIs are required to provide the standard OpenAI completion interface
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello, show me python hello world code"},
            # {"role": "assistant", "content": ...}, # If there is an answer in the history, also include it
        ]
        """

    @abstractmethod
    def acompletion(self, messages: List[Dict]):
        """Asynchronous version of completion
        All GPTAPIs are required to provide the standard OpenAI completion interface
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello, show me python hello world code"},
            # {"role": "assistant", "content": ...}, # If there is an answer in the history, also include it
        ]
        """

    @abstractmethod
    def acompletion_text(self, messages: List[Dict], stream=False) -> str:
        """Asynchronous version of completion. Return str. Support stream-print"""

    def get_choice_text(self, rsp: Dict) -> str:
        """Required to provide the first text of choice"""
        # return rsp.get("choices")[0]["message"]["content"]
        return rsp.choices[0].message.content

    def messages_to_prompt(self, messages: List[Dict]):
        """[{"role": "user", "content": msg}] to user: <msg> etc."""
        return '\n'.join([f"{i['role']}: {i['content']}" for i in messages])

    def messages_to_dict(self, messages):
        """objects to [{"role": "user", "content": msg}] etc."""
        return [i.to_dict() for i in messages]


class RateLimiter:
    """Rate control class, each call goes through wait_if_needed, sleep if rate control is needed"""

    def __init__(self, rpm):
        self.last_call_time = 0
        # Here 1.1 is used because even if the calls are made strictly according to time,
        # they will still be QOS'd; consider switching to simple error retry later
        self.interval = 1.1 * 60 / rpm
        self.rpm = rpm

    def split_batches(self, batch):
        return [batch[i: i + self.rpm] for i in range(0, len(batch), self.rpm)]

    def wait_if_needed(self, num_requests):
        current_time = time.time()
        elapsed_time = current_time - self.last_call_time

        if elapsed_time < self.interval * num_requests:
            remaining_time = self.interval * num_requests - elapsed_time
            LOGGER.info(f"sleep {remaining_time}")
            time.sleep(remaining_time)

        self.last_call_time = time.time()


class Costs(NamedTuple):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost: float
    total_budget: float


def log_and_reraise(retry_state):
    LOGGER.error(f"Retry attempts exhausted. Last exception: {retry_state.outcome.exception()}")
    LOGGER.warning("""
Recommend going to https://deepwisdom.feishu.cn/wiki/MsGnwQBjiif9c3koSJNcYaoSnu4#part-XdatdVlhEojeAfxaaEZcMV3ZniQ
See FAQ 5.8
""")
    raise retry_state.outcome.exception()


class OpenAIGPTAPI(BaseGPTAPI, RateLimiter):
    """
    Check https://platform.openai.com/examples for examples
    """

    def __init__(self):
        self.__init_openai(CONFIG)
        self.llm = openai
        self.model = CONFIG.openai_api_model
        print(CONFIG)
        self.auto_max_tokens = False
        RateLimiter.__init__(self, rpm=self.rpm)

    def __init_openai(self, config):
        print(config)
        openai.api_key = config.openai_api_key
        print(openai.api_key)
        if config.openai_api_base:
            openai.api_base = config.openai_api_base
        if config.openai_api_type:
            openai.api_type = config.openai_api_type
            openai.api_version = config.openai_api_version
            openai.azure_endpoint = config.openai_api_endpoint
        self.rpm = int(config.get("RPM", 10))

        print(openai.azure_endpoint)

        self.client = AzureOpenAI(
            api_version = openai.api_version,
            azure_endpoint = openai.azure_endpoint,
            api_key = openai.api_key,
            )

    def _achat_completion_stream(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(**self._cons_kwargs(messages), stream=True)
        # create variables to collect the stream of chunks
        # print(response.usage.prompt_tokens)
        collected_chunks = []
        collected_messages = []
        # iterate through the stream of events
        for chunk in response:
            collected_chunks.append(chunk)  # save the event response
            choices = chunk.choices

            if len(choices) > 0 and chunk.choices[0].delta.content is not None:
                chunk_message = chunk.choices[0].delta.content # extract the message
                # print(chunk_message)
                collected_messages.append(chunk_message)  # save the message
                # if "content" in chunk_message:
                    # print(chunk_message["content"], end="")

        full_reply_content = "".join([m for m in collected_messages])
        # usage = self._calc_usage(messages, full_reply_content)
        # print(f"full_reply_content: {full_reply_content}")
        return full_reply_content

    def _achat_completion(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(**self._cons_kwargs(messages), stream=False)
        # create variables to collect the stream of chunks
        # print(response.usage.prompt_tokens)
        # iterate through the stream of events
        reply_content = response.choices[0].message.content
        token_costs = response.usage.total_tokens 
        
        return reply_content, token_costs

    def _cons_kwargs(self, messages: List[Dict]) -> Dict:
        import random
        if CONFIG.openai_api_type == "azure":
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.get_max_tokens(messages),
                "temperature": 0.9,
                "seed": random.randint(0, 100000),
            }
        else:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.get_max_tokens(messages),
                "n": 1,
                "stop": None,
                "temperature": 0.5,
            }
        kwargs["timeout"] = 100
        return kwargs

    def _chat_completion(self, messages: List[Dict]) -> Dict:
        rsp = self.client.chat.completions.create(**self._cons_kwargs(messages))
        # self._update_costs(rsp)
        return rsp

    def completion(self, messages: List[Dict]) -> Dict:
        # if isinstance(messages[0], Message):
        #     messages = self.messages_to_dict(messages)
        return self._chat_completion(messages)

    def acompletion(self, messages: List[Dict]) -> Dict:
        # if isinstance(messages[0], Message):
        #     messages = self.messages_to_dict(messages)
        return self._achat_completion(messages)

    def acompletion_text(self, messages: List[Dict], stream=False) -> str:
        """when streaming, print each token in place."""
        if stream:
            return self._achat_completion_stream(messages)
        rsp, token_costs = self._achat_completion(messages)
        return rsp, token_costs

    def _calc_usage(self, messages: List[Dict], rsp: str) -> Dict:
        usage = {}
        if CONFIG.calc_usage:
            try:
                prompt_tokens = count_message_tokens(messages, self.model)
                completion_tokens = count_string_tokens(rsp, self.model)
                usage['prompt_tokens'] = prompt_tokens
                usage['completion_tokens'] = completion_tokens
                return usage
            except Exception as e:
                LOGGER.error("usage calculation failed!", e)
        else:
            return usage

    def get_max_tokens(self, messages: List[Dict]):
        if not self.auto_max_tokens:
            return CONFIG.max_tokens_rsp
        return get_max_completion_tokens(messages, self.model, CONFIG.max_tokens_rsp)


# TODO: GPT4-32k, GPT4, GPT3.5 with a tempreture parameter