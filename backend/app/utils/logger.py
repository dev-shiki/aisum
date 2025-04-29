import logging
from fastapi import Request, Response

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def log_request(request: Request):
    """
    Mencatat request masuk, menghindari error decoding pada file upload.
    """
    try:
        content_type = request.headers.get("content-type", "")
        
        if "multipart/form-data" in content_type:
            logging.info(f"📥 Request: {request.method} {request.url} - Body: [File Upload Detected]")
        else:
            body = await request.body()
            logging.info(f"📥 Request: {request.method} {request.url} - Body: {body.decode(errors='ignore')}")
    
    except Exception as e:
        logging.error(f"❌ Gagal mencatat request: {str(e)}")

async def log_response(response: Response):
    """
    Mencatat response server, menangani streaming response dengan hanya mencatat status_code.
    """
    try:
        logging.info(f"✅ Response: Status {response.status_code}")
    
    except Exception as e:
        logging.error(f"❌ Gagal mencatat response: {str(e)}")
