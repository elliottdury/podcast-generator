import json
from openai import OpenAI
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
import datetime
from typing import Literal, ClassVar, Callable
from .models import PodcastConfig, ChatMessage
from pathlib import Path

class OllamaConfig(BaseModel):
    provider_name: ClassVar[str] = "ollama"
    model_id: str

class OpenRouterConfig(BaseModel):
    provider_name: ClassVar[str] = "openrouter"
    base_url: str | None = "https://openrouter.ai/api/v1"
    model_id: str
    api_key: str

class ScriptBuilder:
    def __init__(
        self,
        generation_config_path: str,
        model_provider_config: OllamaConfig | OpenRouterConfig,
        output_dir_name: str | None = None,
    ):
        with open(generation_config_path) as jf:
            generation_config_raw_json = json.load(jf)
            validated_generation_config_model = PodcastConfig.model_validate(generation_config_raw_json)

        self.generation_config = validated_generation_config_model
        self.model_provider: Literal["ollama", "openrouter"] = (
            model_provider_config.provider_name
        )
        self.model_provider_config = model_provider_config
        self.output_dir_name = output_dir_name if output_dir_name is not None else f"{datetime.datetime.now().strftime("%d%m%Y%H%M%S")}"
        if self.model_provider == "ollama":
            self.generate: Callable[[list[ChatMessage]], str] = self._ollama_generate
        elif self.model_provider == "openrouter":
            self.generate: Callable[[list[ChatMessage]], str] = self._openrouter_generate

    def compose(self):

        base_dir = Path(__file__).resolve().parents[1]
        project_dir = base_dir / self.output_dir_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # super lazy approach but just for poc
        script = []
        for index, chapter in enumerate(self.generation_config.chapters):

            print(f"Writing chapter: {index+1} of {len(self.generation_config.chapters)}")
            chapter_generation_response = self.generate(
                [ChatMessage(
                    role="system",
                    content=self.generation_config.system_prompt
                ),
                ChatMessage(
                    role="user",
                    content=self.generation_config.plot.model_dump_json()
                ),
                ChatMessage(
                    role="user",
                    content=chapter.model_dump_json()
                )
                ]
            )
            script.append(chapter_generation_response)

        complete_script = "\n\n".join(script)

        with open(project_dir / "script.txt", "w") as script_output:
            script_output.write(complete_script)
        
        return complete_script, project_dir

    def _openrouter_generate(self, messages: list[ChatMessage]):
        if self.model_provider != "openrouter":
            raise Exception("Incompatible generation function")

        openrouter_config: OpenRouterConfig = self.model_provider_config

        client = OpenAI(
            base_url=openrouter_config.base_url,
            api_key=openrouter_config.api_key,
        )

        completion = client.chat.completions.create(
            model=openrouter_config.model_id,
            messages=messages
        )
        response = completion.choices[0].message.content

        return response

    def _ollama_generate(self, messages: list[ChatMessage]):
        if self.model_provider != "ollama":
            raise Exception("Incompatible generation function")

        ollama_config: OllamaConfig = self.model_provider_config

        response: ChatResponse = chat(
            model=ollama_config.model_id,
            messages=messages
        )

        response = response.message.content

        return response

# todo: add error handling
# todo: improve how outputs are saved
# todo: make async requests for faster script generation
