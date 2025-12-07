import json
from openai import OpenAI


def read_config(path):
    with open(path) as jf:
        f = json.load(jf)
        return f


def generate_script(model_id: str, model_api_key: str, config: str):
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
                    {"type": "text", "text": json.dumps(config['plot'])},
                ],
            },
        ],
    )
    return completion.choices[0].message.content
