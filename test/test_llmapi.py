import pytest
import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from metaagent.LLMs.llmapi import LLM_API

@pytest.mark.asyncio
async def test_acompletion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages = [{"role": "user", "content": "Hello"}]
    response = await llm.acompletion(messages)
    print(response)
    assert response is not None
    assert isinstance(response.choices[0].message.content, str)
    assert len(response.choices[0].message.content) > 0
    assert response.usage.total_tokens > 0

def test_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages = [{"role": "user", "content": "Hello"}]
    response = llm.completion(messages)
    assert response is not None
    assert isinstance(response.choices[0].message.content, str)
    assert len(response.choices[0].message.content) > 0
    assert response.usage.total_tokens > 0

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
        json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        pytest.fail("Response is not a valid JSON")
    assert len(response.choices[0].message.content) > 0
    assert response.usage.total_tokens > 0


def test_json_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
    ]
    response = llm.json_completion(messages)
    import json
    try:
        json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        pytest.fail("Response is not a valid JSON")
    assert len(response.choices[0].message.content) > 0
    assert response.usage.total_tokens > 0

@pytest.mark.asyncio
async def test_astream_completion():
    llm = LLM_API("deepseek/deepseek-chat")
    messages = [{"role": "user", "content": "Hello"}]
    response = llm.astream_completion(messages)
    async for chunk in response:
        print(chunk)

    
