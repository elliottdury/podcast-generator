# Podcast generator
## Setup
Clone the GitHub Repository.
```
git clone https://github.com/elliottdury/podcast-generator
```

Install Ollama
```
https://ollama.com/download
```

Download a local model, I recommend `Qwen3-4b-2507-Instruct`
```
ollama pull hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M
```
Start the ollama server
```
ollama start
```
Start the local TTS server (make sure you have docker installed)
```
docker compose up -d
```
Run the demo script
```
python -m generate
```
