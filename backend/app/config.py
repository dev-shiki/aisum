import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

class Config:
    WHISPER_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    LLAMA_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    WHISPER_API_KEY = "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"
    LLAMA_API_KEY = "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"
    TEMP_FOLDER = "temp/"
    MAX_SUMMARY_LENGTH = 200
