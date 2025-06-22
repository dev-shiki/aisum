import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

class Config:
<<<<<<< HEAD
    WHISPER_API_URL = os.getenv("WHISPER_API_URL", "https://api.groq.com/openai/v1/audio/transcriptions")
    LLAMA_API_URL = os.getenv("LLAMA_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")
    LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
    TEMP_FOLDER = os.getenv("TEMP_FOLDER", "temp/")
    MAX_SUMMARY_LENGTH = int(os.getenv("MAX_SUMMARY_LENGTH", "200"))

    # Gemini config
    GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_RPM = int(os.getenv("GEMINI_RPM", "15"))
    GEMINI_TPM = int(os.getenv("GEMINI_TPM", "1000000"))
    GEMINI_RPD = int(os.getenv("GEMINI_RPD", "200"))

    # Validasi API keys
    @classmethod
    def validate_config(cls):
        if not cls.WHISPER_API_KEY:
            raise ValueError("WHISPER_API_KEY tidak ditemukan di environment variables")
        # Gemini opsional, tapi warning jika tidak ada
        if not cls.GEMINI_API_KEY:
            print("[WARNING] GEMINI_API_KEY tidak ditemukan di environment variables")
        if not cls.LLAMA_API_KEY:
            print("[INFO] LLAMA_API_KEY tidak ditemukan di environment variables (tidak dipakai jika pakai Gemini)")
=======
    WHISPER_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    LLAMA_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    WHISPER_API_KEY = "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"
    LLAMA_API_KEY = "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"
    TEMP_FOLDER = "temp/"
    MAX_SUMMARY_LENGTH = 200
>>>>>>> ebf96c8bb5f394337221a9323b61a5240a614c4c
