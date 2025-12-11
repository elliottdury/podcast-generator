import json
from openai import OpenAI
from ollama import chat
from ollama import ChatResponse
import datetime

def read_config(path):
    with open(path) as jf:
        f = json.load(jf)
        return f

def generate_script_openrouter(model_id: str, model_api_key: str, config: str, script_output: str | None):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=model_api_key,
    )

    completion = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": config["system_prompt"]},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": str(json.dumps(config['plot']))},
                ],
            },
        ],
    )
    response = completion.choices[0].message.content
    with open(f"{script_output if script_output is not None else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
        f.write(response)
    return response

def generate_script_ollama(model_id: str, config: str, script_output: str | None):
    
    response: ChatResponse = chat(model=model_id, messages=[
        {
            "role": "system",
            "content": str(config["system_prompt"])
        },
        {
            "role": "user",
            "content": str(json.dumps(config['plot']))
        },
    ])

    response = response.message.content
    with open(f"{script_output if script_output is not None else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
        f.write(response)
    return response

# Add ollama support
# Add support for context injection
# Add pydantic ai or instructor