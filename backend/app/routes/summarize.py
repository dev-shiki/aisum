import os
import time
import logging
import shutil
import uuid
import re
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse
from app.services.whisper import transcribe_audio
from app.services.gemini import summarize_with_gemini, detect_content_type
from app.config import Config
import asyncio
import tempfile
import subprocess
from pydantic import BaseModel

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Advanced chunking configuration
MAX_CHUNK_SIZE = 1000  # Maksimal ukuran chunk yang akan dikirim ke API
MAX_SUMMARY_SIZE = 2000  # Maksimal ukuran ringkasan akhir
CHUNK_OVERLAP = 100  # Overlap antar chunks untuk menjaga konteks
MAX_RETRIES = 5  # Maksimum jumlah retry untuk API request
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

router = APIRouter()

# In-memory storage untuk tasks
tasks = {}

class YouTubeRequest(BaseModel):
    youtube_url: str

def validate_youtube_url(url: str) -> bool:
    """Validasi URL YouTube."""
    youtube_patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/v/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+',  # YouTube Shorts
        r'^https?://youtube\.com/shorts/[\w-]+'  # YouTube Shorts tanpa www
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def download_youtube_audio(youtube_url: str, output_dir: str) -> str:
    """
    Download audio from YouTube using yt-dlp and return the file path.
    """
    try:
        logging.info(f"🎬 Starting download for: {youtube_url}")
        logging.info(f"📁 Output directory: {output_dir}")
        
        # Path absolut ke yt-dlp.exe
        yt_dlp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/Scripts/yt-dlp.exe'))
        logging.info(f"🔎 Menggunakan yt-dlp path: {yt_dlp_path}")
        
        # Output file path
        output_path = os.path.join(output_dir, '%(id)s.%(ext)s')
        logging.info(f"📄 Output path pattern: {output_path}")
        
        # Download command dengan optimasi untuk kecepatan
        command = [
            yt_dlp_path,
            '-f', 'bestaudio',  # Ambil kualitas audio terbaik
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '64K',  # Kualitas lebih baik
            '--max-downloads', '1',
            '--no-playlist',
            '--no-check-certificates',  # Skip SSL check untuk kecepatan
            '--no-warnings',
            '--quiet',
            '-o', output_path,
            youtube_url
        ]
        
        logging.info(f"🔧 Command: {' '.join(command)}")
        logging.info(f"🎬 Downloading: {youtube_url}")
        
        # Run dengan timeout 3 menit (lebih pendek)
        result = subprocess.run(command, timeout=180, capture_output=True, text=True)
        logging.info(f"🔚 yt-dlp exited with code: {result.returncode}")
        logging.info(f"📤 yt-dlp stdout: {result.stdout}")
        logging.info(f"📥 yt-dlp stderr: {result.stderr}")
        
        # Find the downloaded file
        files = os.listdir(output_dir)
        logging.info(f"📁 Files in output dir: {files}")
        
        for file in files:
            if file.endswith('.mp3'):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                logging.info(f"✅ Downloaded: {file} ({file_size:.1f} MB)")
                return file_path
        
        logging.error(f"❌ No audio file found after download. All files: {files}")
        raise Exception(f'Audio file not found after download. yt-dlp exit code: {result.returncode}, stdout: {result.stdout}, stderr: {result.stderr}')
        
    except subprocess.TimeoutExpired:
        logging.error("❌ Download timeout - video terlalu panjang atau koneksi lambat")
        raise Exception('Download timeout - video terlalu panjang atau koneksi lambat')
    except Exception as e:
        logging.error(f"❌ Download error: {str(e)}")
        raise Exception(f'Download error: {str(e)}')

@router.post("/summarize/youtube/")
async def summarize_youtube(request: YouTubeRequest):
    """
    Terima link YouTube, download audio, transcribe, dan summarize.
    """
    try:
        youtube_url = request.youtube_url.strip()
        
        logging.info(f"🎬 ===== START YOUTUBE PROCESSING =====")
        logging.info(f"🎬 URL: {youtube_url}")
        
        # Validasi URL
        if not validate_youtube_url(youtube_url):
            logging.error(f"❌ Invalid YouTube URL: {youtube_url}")
            raise HTTPException(status_code=400, detail="URL YouTube tidak valid. Pastikan URL berasal dari YouTube.")
        
        logging.info("✅ URL validation passed")
        
        # Validasi config
        try:
            Config.validate_config()
            logging.info("✅ Config validation passed")
        except ValueError as e:
            logging.error(f"❌ Config validation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
        temp_dir = tempfile.mkdtemp(prefix="yt_", dir="temp")
        logging.info(f"📁 Created temp directory: {temp_dir}")
        
        try:
            logging.info(f"🎬 Memulai proses YouTube: {youtube_url}")
            
            # 1. Download audio
            logging.info("📥 ===== STEP 1: DOWNLOADING AUDIO =====")
            audio_path = download_youtube_audio(youtube_url, temp_dir)
            logging.info(f"✅ Audio downloaded successfully: {audio_path}")
            
            # 2. Transcribe audio
            logging.info("🎤 ===== STEP 2: TRANSCRIBING AUDIO =====")
            transcription = transcribe_audio(audio_path, language="id")
            
            if not transcription.strip():
                logging.error("❌ Transcription is empty or failed")
                raise HTTPException(status_code=400, detail="Transkripsi kosong atau gagal. Pastikan video memiliki audio yang jelas.")
            
            logging.info(f"✅ Transkripsi selesai: {len(transcription)} karakter")
            
            # 3. Summarize dengan progress detail
            logging.info("📝 ===== STEP 3: SUMMARIZING =====")
            content_type = detect_content_type(transcription)
            logging.info(f"🔍 Content type detected: {content_type}")
            
            # Optimasi berdasarkan panjang transkripsi
            if len(transcription) > 10000:  # Transkripsi panjang
                logging.info("📊 Transkripsi panjang terdeteksi, menggunakan chunking...")
                summary = summarize_with_gemini(transcription, content_type=content_type)
            else:  # Transkripsi pendek, langsung summarize
                logging.info("📊 Transkripsi pendek, langsung summarize...")
                summary = summarize_with_gemini(transcription, content_type=content_type)
            
            logging.info("✅ Summarization selesai!")

            # Pastikan summary dikirim sebagai object (dict), bukan string JSON
            summary_obj = summary
            if isinstance(summary, str):
                try:
                    summary_obj = json.loads(summary)
                except Exception:
                    summary_obj = summary

            # 4. Cleanup audio
            logging.info("🧹 ===== STEP 4: CLEANUP =====")
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logging.info(f"🗑️ Deleted audio file: {audio_path}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.info(f"🗑️ Deleted temp directory: {temp_dir}")
            
            # 5. Return result
            logging.info("🎉 ===== YOUTUBE PROCESSING COMPLETED =====")
            return {
                "summary": summary_obj,
                "content_type": content_type,
                "transcription_length": len(transcription),
                "youtube_url": youtube_url,
                "status": "completed",
                "processing_info": {
                    "transcription_chars": len(transcription),
                    "summary_chars": len(str(summary_obj)),
                    "compression_ratio": f"{round(len(str(summary_obj)) / len(transcription) * 100, 2) if transcription else 0}%",
                    "content_type": content_type
                }
            }
            
        except HTTPException:
            # Re-raise HTTP exceptions
            logging.error("❌ HTTP Exception occurred, cleaning up...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
            
        except Exception as e:
            logging.error(f"❌ Unexpected error during processing: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.error(f"❌ YouTube processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal memproses YouTube: {str(e)}")
            
    except HTTPException:
        # Re-raise HTTP exceptions from outer scope
        raise
    except Exception as e:
        logging.error(f"❌ Critical error in summarize_youtube: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error kritis: {str(e)}")

@router.post("/summarize/youtube/test")
async def test_youtube_endpoint(request: YouTubeRequest):
    """
    Test endpoint untuk YouTube tanpa download video asli.
    """
    youtube_url = request.youtube_url.strip()
    
    # Validasi URL
    if not validate_youtube_url(youtube_url):
        raise HTTPException(status_code=400, detail="URL YouTube tidak valid.")
    
    # Return mock data untuk test
    return {
        "summary": "Ini adalah test summary untuk video YouTube. Endpoint berfungsi dengan baik!",
        "content_type": "youtube",
        "transcription_length": 100,
        "youtube_url": youtube_url,
        "status": "completed",
        "test_mode": True
    }

@router.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah file MP3 dan memproses ringkasan.
    """
    # Validasi file
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid")
    
    if not file.filename.lower().endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Hanya file MP3 yang didukung")
    
    # Validasi config
    try:
        Config.validate_config()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    task_id = str(uuid.uuid4())
    unique_filename = f"{task_id}_{file.filename}"
    temp_file_path = os.path.join(Config.TEMP_FOLDER, unique_filename)
    
    # Pastikan folder temp ada
    os.makedirs(Config.TEMP_FOLDER, exist_ok=True)

    try:
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan file: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal menyimpan file")

    tasks[task_id] = {"status": "processing", "message": "Transkripsi sedang berjalan..."}

    async def process_task():
        try:
            logging.info(f"🔍 Task {task_id}: Memulai transkripsi...")
            transcription = transcribe_audio(temp_file_path, language="id")

            if not transcription.strip():
                tasks[task_id] = {"status": "failed", "error": "Transkripsi kosong atau gagal."}
                return

            tasks[task_id]["message"] = "Transkripsi selesai. Memulai proses ringkasan..."
            logging.info(f"✅ Task {task_id}: Transkripsi selesai ({len(transcription)} karakter).")
            
            # Langkah 1: Summarization dengan content type detection
            content_type = detect_content_type(transcription)
            logging.info(f"🔍 Content type detected for task {task_id}: {content_type}")
            
            final_summary = summarize_with_gemini(transcription, content_type=content_type)
            
            tasks[task_id] = {
                "status": "completed",
                "transcription": transcription,
                "summary": final_summary,
                "task_id": task_id,
                "content_type": content_type,
                "metadata": {
                    "original_length": len(transcription),
                    "summary_length": len(final_summary),
                    "compression_ratio": f"{round(len(final_summary) / len(transcription) * 100, 2) if transcription else 0}%",
                    "generated_at": datetime.now().isoformat(),
                    "content_type": content_type,
                    "content_type_detected": True
                }
            }

        except Exception as e:
            logging.error(f"❌ Task {task_id}: Error - {str(e)}")
            tasks[task_id] = {"status": "failed", "error": str(e)}
        finally:
            # Hapus file audio sementara
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logging.info(f"🗑️ Task {task_id}: File audio sementara dihapus.")
                except Exception as e:
                    logging.warning(f"⚠️ Task {task_id}: Gagal menghapus file audio sementara: {str(e)}")

    asyncio.create_task(process_task())
    return {"task_id": task_id, "status": "processing"}

@router.get("/summarize/status/{request_id}")
async def check_status(request_id: str):
    """
    Endpoint untuk memeriksa status pemrosesan berdasarkan task_id.
    """
    if not request_id:
        raise HTTPException(status_code=400, detail="Task ID tidak valid")
    
    task_status = tasks.get(request_id, {"status": "not_found"})
    return task_status

@router.get("/health")
async def health_check():
    """
    Health check untuk API.
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    } 