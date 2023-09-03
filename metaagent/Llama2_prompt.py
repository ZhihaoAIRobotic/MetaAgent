
messages=[{
                "role": "user",
                "content": "How are you doing today?"
            },
            {
                "role": "asisstant",
                "content": "I am fine."
            },
            {
                "role": "user",
                "content": "What is your name?"
            },
            {
                "role": "asisstant",
                "content": "My name is ZIYI."
            },
            {
                "role": "user",
                "content": "What is your age?"
            },
            ]

def llama_v2_prompt(
    messages
):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    BOS, EOS = "<s>", "</s>"
    DEFAULT_SYSTEM_PROMPT = f"""You are a helpful, respectful woman."""

    if messages[0]["role"] != "system":
        messages = [
            {
                "role": "system",
                "content": DEFAULT_SYSTEM_PROMPT,
            }
        ] + messages
    messages = [
        {
            "role": messages[1]["role"],
            "content": B_SYS + messages[0]["content"] + E_SYS + messages[1]["content"],
        }
    ] + messages[2:]

    messages_list = [
        f"{BOS}{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} {EOS}"
        for prompt, answer in zip(messages[::2], messages[1::2])
    ]
    messages_list.append(f"{BOS}{B_INST} {(messages[-1]['content']).strip()} {E_INST}")

    return "".join(messages_list)

re = llama_v2_prompt(messages)

print(re)