import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def summarize_text(text: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": f"Summarize the following webpage:\n\n{text}",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()['response']
