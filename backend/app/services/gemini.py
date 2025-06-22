import requests
import logging
from app.config import Config

def summarize_with_gemini(text: str, system_prompt: str = None) -> str:
    """
    Kirim permintaan ringkasan ke Google Gemini 2.0 Flash API.
    """
    if not Config.GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY tidak tersedia di environment variables")

    url = f"{Config.GEMINI_API_URL}?key={Config.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    prompt = system_prompt or "Ringkas teks berikut dalam bentuk paragraf koheren dan singkat."
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{prompt}\n{text}"}]}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Gemini response format
        summary = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not summary:
            logging.warning(f"[Gemini] Response tidak mengandung ringkasan: {data}")
            return "Ringkasan tidak tersedia."
        return summary
    except Exception as e:
        logging.error(f"[Gemini] Error: {str(e)}")
        raise 