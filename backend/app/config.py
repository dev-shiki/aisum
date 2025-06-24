import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

class Config:
    @property
    def WHISPER_API_URL(self):
        return os.getenv("WHISPER_API_URL", "https://api.groq.com/openai/v1/audio/transcriptions")
    @property
    def WHISPER_API_KEY(self):
        return os.getenv("WHISPER_API_KEY")
    @property
    def TEMP_FOLDER(self):
        return os.getenv("TEMP_FOLDER", "temp/")
    @property
    def MAX_SUMMARY_LENGTH(self):
        return int(os.getenv("MAX_SUMMARY_LENGTH", "200"))
    @property
    def GEMINI_API_URL(self):
        return os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")
    @property
    def GEMINI_API_KEY(self):
        return os.getenv("GEMINI_API_KEY")
    @property
    def GEMINI_RPM(self):
        return int(os.getenv("GEMINI_RPM", "15"))
    @property
    def GEMINI_TPM(self):
        return int(os.getenv("GEMINI_TPM", "1000000"))
    @property
    def GEMINI_RPD(self):
        return int(os.getenv("GEMINI_RPD", "200"))

    @classmethod
    def validate_config(cls):
        if not os.getenv("WHISPER_API_KEY"):
            raise ValueError("WHISPER_API_KEY tidak ditemukan di environment variables")
        if not os.getenv("GEMINI_API_KEY"):
            print("[WARNING] GEMINI_API_KEY tidak ditemukan di environment variables")
