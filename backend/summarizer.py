import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
# OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "granite3.2:2b"


def summarize_text(text: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": f"Summarize the following webpage, using 30 words or less. Be concise, but make sure to capture the key points:\n\n{text}",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        print(f"Error with LLM summarization: {e}")
        return ""
