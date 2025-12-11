import json
from openai import OpenAI
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
import datetime
from typing import Literal

class OllamaConfig(BaseModel):
    provider_name = "ollama"
    model_id: str

class OpenRouterConfig(BaseModel):
    provider_name = "openrouter"
    base_url: str | None = "https://openrouter.ai/api/v1"
    model_id: str
    api_key: str

class ScriptBuilder:
    def __init__(
            self, 
            generation_config_path: str,
            model_provider_config: Literal[OllamaConfig, OpenRouterConfig],
            script_output_name: str | None
        ):
        with open(generation_config_path) as jf:
            f = json.load(jf)
        self.generation_config = f
        self.model_provider: Literal["ollama", "openrouter"] = model_provider_config.provider_name
        self.model_provider_config = model_provider_config
        self.script_output_name = script_output_name

    def compose(self):
        # builds out a script to n recursions using multiple agents etc etc
        return True

    def _validate_generation_config(json_str):
        return True

    def _generate_script_openrouter(self):

        if self.model_provider != "openrouter":
            raise Exception("Incompatible generation function")
        
        openrouter_config: OpenRouterConfig = self.model_provider_config

        client = OpenAI(
            base_url=openrouter_config.base_url,
            api_key=openrouter_config.api_key,
        )

        completion = client.chat.completions.create(
        model=openrouter_config.model_id,
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": self.generation_config["system_prompt"]},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": str(json.dumps(self.generation_config['plot']))},
                ],
            },
        ],
        )
        response = completion.choices[0].message.content
        with open(f"{self.script_output_name if self.script_output_name is not None else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
            f.write(response)
        return response

    def _generate_script_ollama(self):

        if self.model_provider != "ollama":
            raise Exception("Incompatible generation function")

        ollama_config: OllamaConfig = self.model_provider_config

        # also initialize the client here incase ollama is on a different port than usual

        response: ChatResponse = chat(model=ollama_config.model_id, messages=[
        {
            "role": "system",
            "content": str(self.generation_config["system_prompt"])
        },
        {
            "role": "user",
            "content": str(json.dumps(self.generation_config['plot']))
        },
        ])

        response = response.message.content
        with open(f"{self.script_output_name if self.script_output_name is not None else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
            f.write(response)
        return response

# Multi model support will be added but not priority