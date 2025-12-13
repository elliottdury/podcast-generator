from . import (
    OPENROUTER_API_KEY,
    ELEVENLABS_API_KEY,  # noqa: F401
    OPENROUTER_MODEL,  # noqa: F401
    OLLAMA_MODEL,  # noqa: F401
    OLLAMA_PORT,  # noqa: F401
)
from .script import ScriptBuilder, OpenRouterConfig
from .voice import generate_audio_kokoro

def main():
    provider_config = OpenRouterConfig(
        model_id="deepseek/deepseek-v3.2",
        api_key=OPENROUTER_API_KEY
    )
    builder = ScriptBuilder(
        generation_config_path="podcast.json",
        model_provider_config=provider_config
    )
    complete_script, project_dir = builder.compose()
    generate_audio_kokoro(text=complete_script, audio_output=f"{project_dir}/micro_saas_podcast")

if __name__ == "__main__":
    main()
