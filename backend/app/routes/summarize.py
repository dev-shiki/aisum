import os
import time
import logging
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.whisper import transcribe_audio
from app.services.llama import summarize_text
import asyncio
from fastapi.responses import FileResponse

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Max chunk size and max summary size limits
MAX_CHUNK_SIZE = 1000  # Maksimal ukuran chunk yang akan dikirim ke API
MAX_SUMMARY_SIZE = 2000  # Maksimal ukuran ringkasan akhir
MAX_RETRIES = 5  # Maksimum jumlah retry untuk API request

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
def process_with_rate_limit(chunks: list, max_requests_per_minute: int = 30) -> list:
    """
    Memproses teks dalam batch dengan retry otomatis jika terjadi rate limit (429).
    """
    results = []
    request_delay = 60 / max_requests_per_minute  # Delay antara setiap request
    
    for chunk in chunks:
        retries = MAX_RETRIES
        delay = 5
        
        while retries > 0:
            try:
                # Mengirimkan teks ke Llama API untuk mendapatkan ringkasan
                summary = summarize_text([{"role": "system", "content": "Berikut adalah hasil transcibe , Ringkas teks dalam bentuk paragraf koheren dan singkat."}, {"role": "user", "content": chunk}])
                
                if summary:
                    results.append(clean_output_text(summary))
                else:
                    results.append("Ringkasan tidak tersedia.")
                
                time.sleep(request_delay)  # Mengatur delay untuk menghindari overload
                break  # Keluar jika sukses
            except Exception as e:
                logging.error(f"Error summarizing chunk: {str(e)}")
                
                if "429" in str(e):  # Jika kena rate limit, coba ulang dengan delay bertambah
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    retries -= 1
                else:
                    results.append("Error dalam ringkasan.")
                    break
    return results

# Fungsi utama untuk memproses teks dan menghasilkan ringkasan
def summarize_text_batch(text: str) -> str:
    """
    Fungsi utama untuk melakukan ringkasan teks dalam batch.
    """
    # Langkah 1: Chunking Teks
    chunks = split_text_into_chunks(text)
    if not chunks:
        logging.error("Teks kosong setelah chunking.")
        return "Teks kosong setelah chunking."  # Menghindari teks kosong
    
    # Langkah 2: Summarization per batch
    batch_summaries = process_with_rate_limit(chunks)
    
    # Langkah 3: Gabungkan Ringkasan
    combined_summary = " ".join(batch_summaries)
    if not combined_summary.strip():
        logging.error("Ringkasan tidak tersedia setelah proses batch.")
        return "Ringkasan tidak tersedia setelah proses batch."

    # Langkah 4: Tidak perlu ringkasan ulang jika sudah selesai
    return combined_summary  # Langsung kembalikan hasil ringkasan pertama

def create_summary_file(summary: str, task_id: str) -> str:
    """
    Membuat file teks dari ringkasan dan menyimpannya di folder sementara.
    """
    file_path = f"temp/{task_id}_summary.txt"
    with open(file_path, "w") as f:
        f.write(summary)
    return file_path

# --- FastAPI router ---
router = APIRouter()
tasks = {}  # Menyimpan status task berdasarkan task_id

@router.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah file MP3 dan memproses ringkasan.
    """
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Hanya file MP3 yang didukung.")

    task_id = str(uuid.uuid4())
    unique_filename = f"{task_id}_{file.filename}"
    temp_file_path = os.path.join("temp", unique_filename)
    os.makedirs("temp", exist_ok=True)

    with open(temp_file_path, "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    tasks[task_id] = {"status": "processing", "message": "Transkripsi sedang berjalan..."}

    async def process_task():
        try:
            logging.info(f"🔍 Task {task_id}: Memulai transkripsi...")
            transcription = transcribe_audio(temp_file_path, language="id")

            if not transcription.strip():
                tasks[task_id] = {"status": "failed", "error": "Transkripsi kosong."}
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
            }

        except Exception as e:
            tasks[task_id] = {"status": "failed", "error": str(e)}
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logging.info(f"🗑️ Task {task_id}: File sementara dihapus.")

    asyncio.create_task(process_task())
    return {"task_id": task_id}

@router.get("/summarize/status/{request_id}")
async def check_status(request_id: str):
    """
    Endpoint untuk memeriksa status pemrosesan berdasarkan task_id.
    """
    return tasks.get(request_id, {"status": "not_found"})


@router.get("/summarize/download/{task_id}")
async def download_summary(task_id: str):
    """
    Mengunduh file ringkasan.
    """
    summary_file_path = os.path.join(os.getcwd(), 'temp', f'{task_id}_summary.txt')

    # Memastikan file ringkasan ada
    if not os.path.exists(summary_file_path):
        raise HTTPException(status_code=404, detail="File ringkasan tidak ditemukan.")
    
    if not os.access(summary_file_path, os.R_OK):
        raise HTTPException(status_code=403, detail="Tidak dapat mengakses file.")
    
    # Kembalikan file sebagai response
    return FileResponse(summary_file_path, media_type='text/plain', filename=f"{task_id}_summary.txt")