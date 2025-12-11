import os
from dotenv import load_dotenv
from .script import read_config, generate_script_openrouter, generate_script_ollama  # noqa: F401
from .voice import generate_audio_elevenlabs, generate_audio_kokoro  # noqa: F401

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
