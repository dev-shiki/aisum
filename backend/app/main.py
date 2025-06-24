import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes.summarize import router as summarize_router
from app.utils.logger import log_request, log_response
from app.config import Config

# Konfigurasi logging level via environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🚀 Aplikasi FastAPI Dimulai...")
    
    # Validasi konfigurasi saat startup
    try:
        Config.validate_config()
        logging.info("✅ Konfigurasi API keys valid")
    except ValueError as e:
        logging.error(f"❌ Konfigurasi tidak valid: {str(e)}")
        logging.error("Pastikan file .env sudah dibuat dengan API keys yang benar")
        raise e
    
    # Pastikan folder temp ada
    os.makedirs(Config().TEMP_FOLDER, exist_ok=True)
    logging.info(f"✅ Folder temp siap: {Config().TEMP_FOLDER}")
    
    yield
    
    logging.info("🛑 Aplikasi FastAPI Ditutup.")

app = FastAPI(
    title="Meeting Summarizer API",
    description="API untuk transkripsi dan ringkasan audio meeting menggunakan AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for Vue frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "*"  # Temporary untuk development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware for logging requests and responses
# @app.middleware("http")
# async def log_requests_responses(request: Request, call_next):
#     await log_request(request)
#     response = await call_next(request)
#     await log_response(response)
#     return response

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "message": "Meeting Summarizer API is running",
        "version": "1.0.0"
    }

# Include summarize router
app.include_router(summarize_router, prefix="/api")

# Graceful shutdown event
@app.on_event("shutdown")
async def shutdown():
    logging.info("🛑 Aplikasi FastAPI sedang dimatikan, membersihkan resources...")

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
