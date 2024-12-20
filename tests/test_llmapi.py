import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metaagent.llms.llmapi import LLM_API

@pytest.mark.asyncio
async def test_acompletion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages = [{"role": "user", "content": "Hello"}]
    response = await llm.acompletion(messages)
    print(response)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

def test_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages = [{"role": "user", "content": "Hello"}]
    response = llm.completion(messages)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_ajson_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
    ]
    response = await llm.ajson_completion(messages)
    import json
    try:
        json.loads(response)
    except json.JSONDecodeError:
        pytest.fail("Response is not a valid JSON")
    assert len(response) > 0


def test_json_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
    ]
    response = llm.json_completion(messages)
    import json
    try:
        json.loads(response)
    except json.JSONDecodeError:
        pytest.fail("Response is not a valid JSON")
    assert len(response) > 0

@pytest.mark.asyncio
async def test_astream_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages = [{"role": "user", "content": "Hello"}]
    response = llm.astream_completion(messages)
    async for chunk in response:
        print(chunk)

    
