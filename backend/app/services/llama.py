import requests
import logging
import time
from app.config import Config

def summarize_text(conversation_history: list, prompt: str = None) -> str:
    """
    Mengirimkan riwayat percakapan ke Llama API untuk mendapatkan ringkasan teks.
    """
    max_retries = 5  # Maksimum jumlah retry jika kena rate limit
    backoff_factor = 2  # Exponential backoff (delay bertambah setiap kali gagal)
    initial_delay = 2  # Delay awal dalam detik

    # Pastikan prompt hanya ditambahkan sekali (tidak bertumpuk)
    if prompt and not any(msg["role"] == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": prompt})

    for attempt in range(max_retries):
        try:
            response = requests.post(
                Config.LLAMA_API_URL,
                headers={
                    "Authorization": f"Bearer {Config.LLAMA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": conversation_history,
                    "max_tokens": Config.MAX_SUMMARY_LENGTH,
                    "temperature": 0.5,  # Temperatur rendah untuk hasil faktual
                },
                timeout=30,  # Tambahkan timeout agar request tidak menggantung selamanya
            )

            logging.info(f"Llama API Response Status: {response.status_code}")

            # Jika response gagal (misalnya 400, 404, 500), raise exception
            response.raise_for_status()

            # Validasi apakah response JSON memiliki data yang diperlukan
            response_data = response.json()
            logging.info(f"Response Data: {response_data}")  # Menambahkan log untuk memeriksa response

            if "choices" in response_data and response_data["choices"]:
                result = response_data["choices"][0].get("message", {}).get("content", "Ringkasan tidak tersedia.")
                logging.info(f"Ringkasan yang diterima: {result}")  # Log hasil ringkasan
                return result
            else:
                logging.error(f"Unexpected API response format: {response_data}")
                return "Ringkasan tidak tersedia."

        except requests.exceptions.RequestException as e:
            logging.error(f"Llama API request failed: {str(e)}")

            # Jika rate limit (429), gunakan backoff retry
            if response.status_code == 429 or response.status_code in [404, 500]:
                delay = initial_delay * (backoff_factor ** attempt)
                logging.warning(f"Rate limit exceeded or server error. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return f"Error: {str(e)}"  # Return error message agar frontend tahu terjadi masalah

    return "Ringkasan gagal dibuat setelah beberapa percobaan."
