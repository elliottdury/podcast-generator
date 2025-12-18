from . import (
    OPENROUTER_API_KEY,
    ELEVENLABS_API_KEY,  # noqa: F401
    OPENROUTER_MODEL,  # noqa: F401
    OLLAMA_MODEL,  # noqa: F401
    OLLAMA_PORT,  # noqa: F401
)
from .producer import PodcastProducer, OpenRouterConfig, VoiceOverConfigKokoro, RAGConfig
from pathlib import Path

def main():
    language_model_provider_config = OpenRouterConfig(
        base_url="https://openrouter.ai/api/v1",
        model_id="deepseek/deepseek-v3.2",
        api_key=OPENROUTER_API_KEY
    )
    tts_model_provider_config = VoiceOverConfigKokoro(
        voice="af_heart"
    )
    producer = PodcastProducer(
        project_dir=Path(__file__).resolve().parent.parent / "saas-podcast",
        language_model_provider_config=language_model_provider_config,
        tts_model_provider_config=tts_model_provider_config,
        rag_config=RAGConfig(n_results=2)
    )
    #print(producer.chroma_collection.query(query_texts=["pricing"], n_results=2))
    #print(producer.ingest_reference_txts())
    #producer.reset_project_chroma_collection()
    producer.ingest_reference_txts()
    script = producer.write_script()
    producer.record_and_save(script)

if __name__ == "__main__":
    main()
