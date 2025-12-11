import os
from . import (
    OPENROUTER_API_KEY,
    ELEVENLABS_API_KEY,
    OPENROUTER_MODEL,
    OLLAMA_MODEL,
    OLLAMA_PORT,
    read_config,
    generate_script_openrouter,
    generate_script_ollama,
    generate_audio_elevenlabs,
    generate_audio_kokoro
)


def main():
    config = read_config("podcast.json")
    # script = generate_script_openrouter(model_id=OPENROUTER_MODEL, model_api_key=OPENROUTER_API_KEY, config=config, script_output="my_podcast")
    script = generate_script_ollama(model_id=OLLAMA_MODEL, config=config, script_output="my_podcast")
    # generate_audio_elevenlabs(eleven_labs_api_key=ELEVENLABS_API_KEY, text=script, audio_output="my_podcast")
    generate_audio_kokoro(text=script, audio_output="my_podcast")



if __name__ == "__main__":
    main()
