import os
from dotenv import load_dotenv
from .script import read_config, generate_script  # noqa: F401
from .voice import generate_audio_elevenlabs, generate_audio_kokoro  # noqa: F401

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
LANGUAGE_MODEL_IDENTIFIER = os.getenv("LANGUAGE_MODEL_IDENTIFIER")
