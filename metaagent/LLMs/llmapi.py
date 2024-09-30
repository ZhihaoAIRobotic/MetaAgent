import litellm
import os
from litellm.integrations.custom_logger import CustomLogger
from metaagent.logs import logger


class CustomHandler(CustomLogger):
    def __init__(self):
        self.user_id = None
        super().__init__()

    def log_pre_api_call(self, model, messages, kwargs):
        # log uid, model, messages, kwargs
        if self.user_id:
            logger.info(f"User ID: {self.user_id} Model: {model} Input Messages: {messages}")
        else:
            logger.info(f"Model: {model} Input Messages: {messages}")

    def log_success_event(self, kwargs, response_obj, start_time, end_time): 
        if self.user_id:
            logger.info(f"User ID: {self.user_id}, Total Tokens: {response_obj.usage.total_tokens}")
        else:
            logger.info(f"Total Tokens: {response_obj.usage.total_tokens}")
        if self.user_id:
            logger.info(f"User ID: {self.user_id}, Output Messages: {response_obj.choices[0].message.content}")
        else:
            logger.info(f"Output Messages: {response_obj.choices[0].message.content}")

    def log_failure_event(self, kwargs, response_obj, start_time, end_time): 
        logger.error(f"Error: {response_obj}")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        if self.user_id:
            logger.info(f"User ID: {self.user_id}, Total Tokens: {response_obj.usage.total_tokens}")
        else:
            logger.info(f"Total Tokens: {response_obj.usage.total_tokens}")
        if self.user_id:
            logger.info(f"User ID: {self.user_id}, Output Messages: {response_obj.choices[0].message.content}")
        else:
            logger.info(f"Output Messages: {response_obj.choices[0].message.content}")

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        logger.error(f"Error: {response_obj}")


class LLM_API:
    def __init__(self, model_name):
        self.model_name = model_name
        self.logger = CustomHandler()

    def completion(self, messages, user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = litellm.completion(model=self.model_name, messages=messages, num_retries=3)
        return response
    
    async def acompletion(self, messages, user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = await litellm.acompletion(model=self.model_name, messages=messages, num_retries=3)
        return response

    def json_completion(self, messages, user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = litellm.completion(model=self.model_name, response_format={ "type": "json_object" }, messages=messages, num_retries=3)
        return response
    
    async def ajson_completion(self, messages, user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = await litellm.acompletion(model=self.model_name, response_format={ "type": "json_object" }, messages=messages, num_retries=3)
        return response
    
    async def astream_completion(self, messages, user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = await litellm.acompletion(model=self.model_name, messages=messages, stream=True, stream_options={"include_usage": True}, num_retries=3)
        async for chunk in response: 
            yield chunk
