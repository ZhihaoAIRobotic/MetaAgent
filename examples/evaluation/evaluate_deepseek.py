import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metaagent.LLMs.llmapi import LLM_API
from metaagent.evaluation.gsm8k import GSM8K
# print("Hello")

class Agent:
    def __init__(self, llm: LLM_API):
        self.llm = llm

    def generate(self, prompt: str):
        llm_input = [{"role": "user", "content": prompt}]
        return self.llm.completion(llm_input)
    

llm = LLM_API("deepseek/deepseek-chat")
agent = Agent(llm)

res = agent.generate("Hello")
print(res)
gsm8k = GSM8K(n_shots=3, enable_cot=True, n_problems=3)
# gsm8k.load_benchmark_dataset()
gsm8k.evaluate(agent)
