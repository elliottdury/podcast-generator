from elevenlabs.client import ElevenLabs
from elevenlabs.play import play, save
from pydantic import BaseModel
import datetime

class VoiceOverConfig(BaseModel):
    """
    Docstring for VoiceOverConfig
    """

    voice_id: str
    model_id: str
    output_format: str


def generate_audio(
    eleven_labs_api_key: str,
    text: str,
    config: VoiceOverConfig = VoiceOverConfig(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    ),
):
    elevenlabs = ElevenLabs(api_key=eleven_labs_api_key)

    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=config.voice_id,
        model_id=config.model_id,
        output_format=config.output_format,
    )
    save(audio=audio, filename=f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
