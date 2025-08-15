import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "granite3.2:2b"


def summarize_text(text: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": f"Summarize the following webpage, using 30 words or less. Be concise, but make sure to capture the key points:\n\n{text}",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()['response']
