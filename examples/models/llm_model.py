import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from metaagent.llms.llmapi import LLM_API


llm = LLM_API('gpt-4o')
response = llm.generate('hi')
print(response)
