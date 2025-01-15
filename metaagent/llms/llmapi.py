import litellm
from typing import Dict, List, Optional, Union
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
    # this also support multi-modal language models, such as gpt-4o-mini and gpt-4o.
    def __init__(self, model_name: str, base_url: str = None, temperature: float = 0.5):
        self.model_name = model_name
        self.logger = CustomHandler()
        self.base_url = base_url
        self.temperature = temperature

    def generate(self, prompt: Optional[Union[str, list[str]]]):
        if isinstance(prompt, list):
            prompt = prompt[0]
        messages = [{"role": "user", "content": prompt}]
        litellm.callbacks = [self.logger]
        
        response = litellm.completion(model=self.model_name, messages=messages, num_retries=3, base_url=self.base_url, temperature=self.temperature)
        return response.choices[0].message.content

    def completion(self, messages: List[Dict[str, str]], user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = litellm.completion(model=self.model_name, messages=messages, num_retries=3, base_url=self.base_url, temperature=self.temperature)
        return response.choices[0].message.content
    
    async def acompletion(self, messages: List[Dict[str, str]], user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = await litellm.acompletion(model=self.model_name, messages=messages, num_retries=3, base_url=self.base_url, temperature=self.temperature)
        return response.choices[0].message.content

    def json_completion(self, messages: List[Dict[str, str]], user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = litellm.completion(model=self.model_name, response_format={ "type": "json_object" }, messages=messages, num_retries=3, base_url=self.base_url, temperature=self.temperature)
        return response.choices[0].message.content
    
    async def ajson_completion(self, messages: List[Dict[str, str]], user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = await litellm.acompletion(model=self.model_name, response_format={ "type": "json_object" }, messages=messages, num_retries=3, base_url=self.base_url, temperature=self.temperature)
        return response.choices[0].message.content
    
    async def astream_completion(self, messages: List[Dict[str, str]], user_id: str = None):
        if user_id:
            self.logger.user_id = user_id
        litellm.callbacks = [self.logger]
        response = await litellm.acompletion(model=self.model_name, messages=messages, stream=True, stream_options={"include_usage": True}, num_retries=3, base_url=self.base_url, temperature=self.temperature)
        async for chunk in response: 
            if chunk['choices'][0]['delta']['content'] is None:
                continue
            yield chunk['choices'][0]['delta']['content']


async def main():
    llm = LLM_API("gpt-4o-mini", base_url="https://api.zhizengzeng.com/v1/chat/completions")
#     messages = [
#     {"role": "system", "content": "You are a helpful assistant. Help me with my math homework!"}, # <-- This is the system message that provides context to the model
#     {"role": "user", "content": "Hello! Could you solve 2+2?"}  # <-- This is the user message for which the model will generate a response
#   ]
    messages=[
        {
            "role": "user",
            "content": [
                            {
                                "type": "text",
                                "text": "What’s in this image?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                "url": "https://res.cloudinary.com/benjamincrozat-com/image/fetch/c_scale,f_webp,q_auto,w_1200/https://github.com/user-attachments/assets/80b40164-bace-4d89-9f09-136e708e5e8e"
                                }
                            }
                        ]
        }
    ]
    res = ''
    
    async for chunk in llm.astream_completion(messages):
        if chunk is not None:
            res += chunk
    print("res", res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())