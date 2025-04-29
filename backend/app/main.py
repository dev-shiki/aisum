import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes.summarize import router as summarize_router
from app.utils.logger import log_request, log_response

# Konfigurasi logging level via environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🚀 Aplikasi FastAPI Dimulai...")
    yield
    logging.info("🛑 Aplikasi FastAPI Ditutup.")

app = FastAPI(lifespan=lifespan)

# CORS for Vue frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for logging requests and responses
@app.middleware("http")
async def log_requests_responses(request: Request, call_next):
    await log_request(request)
    response = await call_next(request)
    await log_response(response)
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
