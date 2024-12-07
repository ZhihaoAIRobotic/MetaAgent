# g1: Using Llama-3.1 70b on Groq to create o1-like reasoning chains https://github.com/bklieger-groq/g1/tree/main

from metaagent.prompts.g1_prompt import G1_SYSTEM_PROMPT, G1_FINAL_ANSWER_PROMPT
from metaagent.LLMs.llmapi import LLM_API
import json

class G1:
    def __init__(self, model_name: str):
        self.llm = LLM_API(model_name)

    def reason(self, instruction: str, maximum_steps: int = 25):
        messages = [
        {"role": "system", "content": G1_SYSTEM_PROMPT},
        {"role": "user", "content": instruction},
        {"role": "assistant", "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem."}
    ]
    
        steps = []
        step_count = 1
        
        while True:
            step_data = self.llm.ajson_completion(messages) # Make sure the LLM supports JSON completion

            step_data = json.loads(step_data)
            
            steps.append((f"Step {step_count}: {step_data['title']}", step_data['content']))
            
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if step_data['next_action'] == 'final_answer' or step_count > maximum_steps: # Maximum of 25 steps to prevent infinite thinking time. Can be adjusted.
                break
            
            step_count += 1
    
            # Yield after each step for Streamlit to update
            yield steps, None  
    
        # Generate final answer
        messages.append({"role": "user", "content": G1_FINAL_ANSWER_PROMPT})
        
        final_data = self.llm.acompletion(messages)
        
        steps.append(("Final Answer", final_data))
    
        yield steps
