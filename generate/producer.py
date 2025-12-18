import json
from openai import OpenAI
from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel
import datetime
from typing import Literal, ClassVar, Callable
from .models import PodcastConfig, ChatMessage
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs.play import save
import chromadb
import hashlib

class OllamaConfig(BaseModel):
    provider_name: ClassVar[str] = "ollama"
    model_id: str

class OpenRouterConfig(BaseModel):
    provider_name: ClassVar[str] = "openrouter"
    base_url: str | None = "https://openrouter.ai/api/v1"
    model_id: str
    api_key: str

class VoiceOverConfigElevenLabs(BaseModel):
    """
    Docstring for VoiceOverConfig
    """
    provider_name: ClassVar[str] = "elevenlabs"
    voice_id: str # e.g. JBFqnCBsd6RMkjVDRZzb
    model_id: str # e.g. eleven_multilingual_v2
    output_format: str # mp3_44100_128
    api_key: str

class VoiceOverConfigKokoro(BaseModel):
    """
    Docstring for VoiceOverConfig
    """
    provider_name: ClassVar[str] = "kokoro"
    voice: str # e.g. af_heart
    api_key: str = "not-needed"

class RAGConfig(BaseModel):
    n_results: int | None = 2

class PodcastProducer:
    def __init__(
        self,
        project_dir: str,
        language_model_provider_config: OllamaConfig | OpenRouterConfig,
        tts_model_provider_config: VoiceOverConfigElevenLabs | VoiceOverConfigKokoro,
        rag_config: RAGConfig
    ):
        self.project_dir = project_dir
        # add error handling
        with open(f"{project_dir}/podcast.json") as jf:
            generation_config_raw_json = json.load(jf)
            validated_generation_config_model = PodcastConfig.model_validate(generation_config_raw_json)

        self.generation_config = validated_generation_config_model
        self.language_model_provider_config = language_model_provider_config
        self.language_model_provider: Literal["ollama", "openrouter"] = (
            language_model_provider_config.provider_name
        )
        self.tts_model_provider_config = tts_model_provider_config
        self.tts_model_provider: Literal["elevenlabs", "kokoro"] = (
            tts_model_provider_config.provider_name
        )
        if self.language_model_provider == "ollama":
            self.generate_text: Callable[[list[ChatMessage]], str] = self._ollama_generate
        elif self.language_model_provider == "openrouter":
            self.generate_text: Callable[[list[ChatMessage]], str] = self._openrouter_generate
        if self.tts_model_provider == "elevenlabs":
            self.generate_audio: Callable[[str], None] = self._generate_audio_elevenlabs
        elif self.tts_model_provider == "kokoro":
            self.generate_audio: Callable[[str], None] = self._generate_audio_kokoro

        self.rag_config = rag_config

        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        self.chroma_collection_name = str(self.project_dir).split("/")[-1]
        self.chroma_collection = self.chroma_client.get_or_create_collection(self.chroma_collection_name)

    def ingest_reference_txts(self):
        for file_path in (self.project_dir / "reference").glob("*.txt"):
            with open(file_path, "r") as file:
                for raw_line in file.readlines():
                    line = raw_line.strip()
                    # dont want empty lines or titles
                    if (not line) or (len(line.split()) < 6):
                        continue
                    line_hash = hashlib.sha256(line.encode()).hexdigest()
                    self.chroma_collection.upsert(
                        ids=[str(line_hash)],
                        documents=[line]
                    )
                    print(f"Ingested line: {str(line_hash)} from document: {file_path}")
        
        return self.chroma_collection.count()
        # now use this and query it with the config description for a specific chapter and also store the chroma client on the podcast producer

    def reset_project_chroma_collection(self):
        self.chroma_client.delete_collection(self.chroma_collection_name)
        self.chroma_collection = self.chroma_client.get_or_create_collection(self.chroma_collection_name)
        print(self.chroma_collection.count())

    def write_script(self):

        # super lazy approach but just for poc
        script = []
        for index, chapter in enumerate(self.generation_config.chapters):
            
            chapter_reference_material = self.chroma_collection.query(
                query_texts=[chapter.chapter_summary],
                n_results=self.rag_config.n_results
            )

            print(f"Writing chapter: {index+1} of {len(self.generation_config.chapters)}")

            generation_prompt_messages = [ChatMessage(
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
        
            if len(chapter_reference_material["documents"]) > 1:
                generation_prompt_messages.append(
                    ChatMessage(
                        role="user",
                        content=f"REFERENCE MATERIAL: \n{"\n".join(chapter_reference_material["documents"])}"
                    )
                )

            chapter_generation_response = self.generate_text(
                generation_prompt_messages
            )
            script.append(chapter_generation_response)

        complete_script = "\n\n".join(script)

        with open(self.project_dir / "script.txt", "w") as script_output:
            script_output.write(complete_script)
        
        return complete_script

    def record_and_save(self, text):
        self.generate_audio(text)
        return None

    def _openrouter_generate(self, messages: list[ChatMessage]):
        if self.language_model_provider != "openrouter":
            raise Exception("Incompatible generation function")

        openrouter_config: OpenRouterConfig = self.language_model_provider_config

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
        if self.language_model_provider != "ollama":
            raise Exception("Incompatible generation function")

        ollama_config: OllamaConfig = self.language_model_provider_config

        response: ChatResponse = chat(
            model=ollama_config.model_id,
            messages=messages
        )

        response = response.message.content

        return response
    
    def _generate_audio_elevenlabs(
        self,
        text: str
    ):
        if self.tts_model_provider != "elevenlabs":
            raise Exception("Incompatible generation function")

        elevenlabs_config: VoiceOverConfigElevenLabs = self.tts_model_provider_config

        elevenlabs = ElevenLabs(api_key=elevenlabs_config.api_key)

        audio = elevenlabs.text_to_speech.convert(
            text=text,
            voice_id=elevenlabs_config.voice_id,
            model_id=elevenlabs_config.model_id,
            output_format=elevenlabs_config.output_format,
        )
        save(audio=audio, filename=f"{self.project_dir}/podcast.mp3")

    def _generate_audio_kokoro(
        self,
        text: str,
    ):
        if self.tts_model_provider != "kokoro":
            raise Exception("Incompatible generation function")
        
        kokoro_config: VoiceOverConfigKokoro = self.tts_model_provider_config

        client = OpenAI(
            base_url="http://localhost:8880/v1", api_key=kokoro_config.api_key
        )

        with client.audio.speech.with_streaming_response.create(
            model="kokoro",
            voice=kokoro_config.voice,
            input=text
        ) as response:
            response.stream_to_file(f"{self.project_dir}/podcast.mp3")

# todo: add error handling
# todo: improve how outputs are saved
# todo: make async requests for faster script generation
