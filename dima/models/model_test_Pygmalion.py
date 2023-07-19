# Load model directly
# from transformers import AutoTokenizer, AutoModelForCausalLM

# Use a pipeline as a high-level helper
# from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("PygmalionAI/pygmalion-6b")
model = AutoModelForCausalLM.from_pretrained("PygmalionAI/pygmalion-6b", device_map="auto")

prompt = "Girlfriend's Persona: She is a very cute girlfriend.S\
<START> \
[DIALOGUE HISTORY] \
You: hi, dear, \
Girlfriend: hi, dear \
You: do you want to go for dinner with me? \
Girlfriend: \
"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens=15)

res = tokenizer.batch_decode(outputs, skip_special_tokens=True)
print(res)

