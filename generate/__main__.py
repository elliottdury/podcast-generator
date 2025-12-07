import os
from . import (
    OPENROUTER_API_KEY,
    ELEVENLABS_API_KEY,
    LANGUAGE_MODEL_IDENTIFIER,
    read_config,
    generate_script,
    generate_audio
)


def main():
    config = read_config("podcast.json")
    script = generate_script(LANGUAGE_MODEL_IDENTIFIER, OPENROUTER_API_KEY, config=config)
    generate_audio(ELEVENLABS_API_KEY, script)



if __name__ == "__main__":
    main()
