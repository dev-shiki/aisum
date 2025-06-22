import os
import time
import logging
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.whisper import transcribe_audio
from app.services.llama import summarize_text
from app.config import Config
import asyncio
from app.services.gemini import summarize_with_gemini

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Max chunk size and max summary size limits
MAX_CHUNK_SIZE = 1000  # Maksimal ukuran chunk yang akan dikirim ke API
MAX_SUMMARY_SIZE = 2000  # Maksimal ukuran ringkasan akhir
MAX_RETRIES = 5  # Maksimum jumlah retry untuk API request
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

# Fungsi untuk membagi teks menjadi chunks cerdas berdasarkan kalimat
def split_text_into_chunks(text: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> list:
    """
    Memecah teks panjang menjadi bagian kecil berdasarkan kalimat agar tetap memiliki konteks.
    """
    sentences = text.split(". ")  # Memecah berdasarkan kalimat (tanda titik diikuti spasi)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 > max_chunk_size:  # +2 untuk ". " separator
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += ". " + sentence
            else:
                current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# Fungsi untuk membersihkan hasil ringkasan
def clean_output_text(summary: str) -> str:
    """
    Membersihkan teks hasil ringkasan agar lebih rapi.
    """
    if not summary:
        return "Ringkasan tidak tersedia."
    return " ".join(summary.replace("\n", " ").split())

# Fungsi utama untuk memproses per batch dengan retry otomatis
def process_with_gemini_rate_limit(chunks: list) -> list:
    """
    Memproses teks dalam batch dengan rate limit Gemini (RPM, TPM, RPD).
    """
    results = []
    request_delay = 60 / Config.GEMINI_RPM  # Delay antar request (detik)
    used_tokens = 0
    max_tokens = Config.GEMINI_TPM
    for chunk in chunks:
        retries = MAX_RETRIES
        delay = 5
        while retries > 0:
            try:
                summary = summarize_with_gemini(chunk)
                used_tokens += len(chunk.split())
                if used_tokens > max_tokens:
                    logging.warning("[Gemini] Token limit tercapai, menunggu reset...")
                    time.sleep(60)  # Tunggu 1 menit
                    used_tokens = 0
                if summary:
                    results.append(clean_output_text(summary))
                else:
                    results.append("Ringkasan tidak tersedia.")
                time.sleep(request_delay)
                break
            except Exception as e:
                logging.error(f"[Gemini] Error summarizing chunk: {str(e)}")
                if "429" in str(e):
                    time.sleep(delay)
                    delay *= 2
                    retries -= 1
                else:
                    results.append("Error dalam ringkasan.")
                    break
    return results

# Fungsi utama untuk memproses teks dan menghasilkan ringkasan
def summarize_text_batch(text: str) -> str:
    """
    Fungsi utama untuk melakukan ringkasan teks dalam batch (pakai Gemini).
    """
    chunks = split_text_into_chunks(text)
    if not chunks:
        logging.error("Teks kosong setelah chunking.")
        return "Teks kosong setelah chunking."
    batch_summaries = process_with_gemini_rate_limit(chunks)
    combined_summary = " ".join(batch_summaries)
    if not combined_summary.strip():
        logging.error("Ringkasan tidak tersedia setelah proses batch.")
        return "Ringkasan tidak tersedia setelah proses batch."
    return combined_summary

def create_summary_file(summary: str, task_id: str) -> str:
    """
    Membuat file teks dari ringkasan dan menyimpannya di folder sementara.
    """
    # Pastikan folder temp ada
    os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
    
    file_path = os.path.join(Config.TEMP_FOLDER, f"{task_id}_summary.txt")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(summary)
        logging.info(f"✅ File ringkasan berhasil dibuat: {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"❌ Gagal membuat file ringkasan: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal membuat file ringkasan")

# --- FastAPI router ---
router = APIRouter()
tasks = {}  # Menyimpan status task berdasarkan task_id

@router.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah file MP3 dan memproses ringkasan.
    """
    # Validasi file
    validate_upload_file(file)
    
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
            
            # Langkah 1: Summarization
            final_summary = summarize_text_batch(transcription)
            # Membuat file ringkasan
            summary_file_path = create_summary_file(final_summary, task_id)
            
            tasks[task_id] = {
                "status": "completed",
                "transcription": transcription,
                "summary": final_summary,
                "summary_file": summary_file_path,
                "task_id": task_id,  # Tambahkan task_id untuk frontend
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
    
    # Jika task completed, tambahkan download URL
    if task_status.get("status") == "completed" and task_status.get("summary_file"):
        task_status["download_url"] = f"/api/summarize/download/{request_id}"
    
    return task_status

@router.get("/summarize/download/{task_id}")
async def download_summary(task_id: str):
    """
    Mengunduh file ringkasan.
    """
    if not task_id:
        raise HTTPException(status_code=400, detail="Task ID tidak valid")
    
    # Cek apakah task ada dan completed
    task_status = tasks.get(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="Task tidak ditemukan")
    
    if task_status.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Task belum selesai diproses")
    
    summary_file_path = task_status.get("summary_file")
    if not summary_file_path:
        raise HTTPException(status_code=404, detail="File ringkasan tidak ditemukan dalam task")

    # Validasi path file
    if not os.path.exists(summary_file_path):
        raise HTTPException(status_code=404, detail="File ringkasan tidak ditemukan di server")
    
    if not os.access(summary_file_path, os.R_OK):
        raise HTTPException(status_code=403, detail="Tidak dapat mengakses file ringkasan")
    
    try:
        # Kembalikan file sebagai response dengan nama file yang lebih user-friendly
        filename = f"summary_{task_id}.txt"
        return FileResponse(
            path=summary_file_path, 
            media_type='text/plain', 
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logging.error(f"❌ Error saat download file {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal mengunduh file")

# Cleanup endpoint untuk menghapus file lama (opsional)
@router.delete("/summarize/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """
    Membersihkan file dan data task yang sudah selesai.
    """
    if not task_id:
        raise HTTPException(status_code=400, detail="Task ID tidak valid")
    
    task_status = tasks.get(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="Task tidak ditemukan")
    
    # Hapus file ringkasan jika ada
    summary_file_path = task_status.get("summary_file")
    if summary_file_path and os.path.exists(summary_file_path):
        try:
            os.remove(summary_file_path)
            logging.info(f"🗑️ File ringkasan dihapus: {summary_file_path}")
        except Exception as e:
            logging.warning(f"⚠️ Gagal menghapus file ringkasan: {str(e)}")
    
    # Hapus task dari memory
    if task_id in tasks:
        del tasks[task_id]
    
    return {"message": "Task berhasil dibersihkan"}

# Validasi file upload
def validate_upload_file(file: UploadFile) -> None:
    """
    Validasi file yang diupload
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid")
    
    if not file.filename.lower().endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Hanya file MP3 yang didukung")
    
    # Cek content type
    if file.content_type not in ['audio/mp3', 'audio/mpeg', 'audio/mp4']:
        raise HTTPException(status_code=400, detail="Tipe file tidak didukung")
    
    # Cek ukuran file (max 50MB)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Ukuran file terlalu besar. Maksimal {MAX_FILE_SIZE // (1024*1024)}MB"
        )