from elevenlabs.client import ElevenLabs
from elevenlabs.play import save
from openai import OpenAI
from pydantic import BaseModel
import datetime

class VoiceOverConfigElevenLabs(BaseModel):
    """
    Docstring for VoiceOverConfig
    """

    voice_id: str
    model_id: str
    output_format: str


def generate_audio_elevenlabs(
    *,
    eleven_labs_api_key: str,
    text: str,
    config: VoiceOverConfigElevenLabs = VoiceOverConfigElevenLabs(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    ),
    audio_output: str | None
):
    elevenlabs = ElevenLabs(api_key=eleven_labs_api_key)

    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=config.voice_id,
        model_id=config.model_id,
        output_format=config.output_format,
    )
    save(audio=audio, filename=f"{audio_output if audio_output is not None else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")

class VoiceOverConfigKokoro(BaseModel):
    """
    Docstring for VoiceOverConfig
    """
    voice: str

def generate_audio_kokoro(
    *,
    text: str,
    config: VoiceOverConfigKokoro = VoiceOverConfigKokoro(
        voice="af_heart",
    ),
    audio_output: str | None
):
    client = OpenAI(
        base_url="http://localhost:8880/v1", api_key="not-needed"
    )

    with client.audio.speech.with_streaming_response.create(
        model="kokoro",
        voice=config.voice,
        input=text
    ) as response:
        response.stream_to_file(f"{audio_output if audio_output is not None else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")