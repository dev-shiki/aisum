# Meeting Summarizer

Aplikasi web untuk transkripsi dan ringkasan audio meeting menggunakan AI. Aplikasi ini menggunakan Whisper API untuk speech-to-text dan Llama/Gemini API untuk text summarization.

## 🚀 Features

- **Audio Transcription**: Konversi file MP3 ke teks menggunakan Whisper AI
- **AI Summarization**: Ringkasan otomatis menggunakan Llama/Gemini AI
- **Real-time Processing**: Status tracking real-time dengan polling
- **File Download**: Download hasil ringkasan dalam format TXT
- **Responsive Design**: UI yang responsif dan user-friendly
- **Error Handling**: Penanganan error yang komprehensif

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Whisper API** - Speech-to-text transcription
- **Llama/Gemini API** - Text summarization
- **Python-dotenv** - Environment variable management
- **Uvicorn** - ASGI server

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Axios** - HTTP client
- **Vue Router** - Client-side routing
- **Vuex** - State management
- **CSS3** - Modern styling dengan Flexbox/Grid

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- npm atau yarn
- API keys untuk Whisper dan Llama/Gemini (Groq/Google)

## 🔧 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd meeting-summarizer
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env file dengan API keys Anda
# WHISPER_API_KEY=your_whisper_api_key
# LLAMA_API_KEY=your_llama_api_key
# GEMINI_API_KEY=your_gemini_api_key
```

### 3. Frontend Setup

```bash
cd ../meeting-summarizer

# Install dependencies
npm install
```

## 🚀 Running the Application

### 1. Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di: http://localhost:8000

### 2. Start Frontend Development Server
```bash
cd ../meeting-summarizer
npm run serve
```

Frontend akan berjalan di: http://localhost:5173 (atau port lain sesuai config)

### 3. Build for Production
```bash
npm run build
```

### 4. Lint & Fix Files
```bash
npm run lint
```

## 📝 Catatan
- Pastikan API key sudah benar di file `.env`.
- Untuk konfigurasi lebih lanjut, lihat dokumentasi di masing-masing folder.

Jika ada masalah atau pertanyaan, silakan buat issue di repository ini.

## 📁 Project Structure

```
meeting-summarizer/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── summarize.py      # API endpoints
│   │   ├── services/
│   │   │   ├── whisper.py        # Whisper API integration
│   │   │   └── llama.py          # Llama API integration
│   │   ├── utils/
│   │   │   └── logger.py         # Logging utilities
│   │   ├── config.py             # Configuration management
│   │   └── main.py               # FastAPI application
│   ├── temp/                     # Temporary files storage
│   ├── requirements.txt          # Python dependencies
│   └── env.example               # Environment variables template
└── meeting-summarizer/
    ├── src/
    │   ├── components/
    │   │   └── FileUpload.vue    # Main upload component
    │   ├── assets/
    │   │   └── css/
    │   │       └── global-styles.css
    │   ├── App.vue               # Root component
    │   └── main.js               # Vue application entry
    ├── package.json              # Node.js dependencies
    └── README.md                 # This file
```

## 🔌 API Endpoints

### POST `/api/summarize/`
Upload file MP3 untuk diproses
- **Request**: Multipart form data dengan file MP3
- **Response**: `{"task_id": "uuid", "status": "processing"}`

### GET `/api/summarize/status/{task_id}`
Cek status pemrosesan
- **Response**: Status task (processing/completed/failed)

### GET `/api/summarize/download/{task_id}`
Download file ringkasan
- **Response**: File TXT untuk diunduh

### DELETE `/api/summarize/cleanup/{task_id}`
Hapus file dan data task
- **Response**: Konfirmasi cleanup

## 🔒 Environment Variables

Buat file `.env` di folder `backend/` dengan variabel berikut:

```env
# API Configuration
WHISPER_API_URL=https://api.groq.com/openai/v1/audio/transcriptions
LLAMA_API_URL=https://api.groq.com/openai/v1/chat/completions

# API Keys (Required)
WHISPER_API_KEY=your_whisper_api_key_here
LLAMA_API_KEY=your_llama_api_key_here

# Application Configuration
TEMP_FOLDER=temp/
MAX_SUMMARY_LENGTH=200

# Server Configuration
PORT=8000
LOG_LEVEL=INFO
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
# TODO: Add pytest tests
```

### Frontend Testing
```bash
cd meeting-summarizer
npm run lint
```

## 🚀 Deployment

### Backend Deployment
1. Setup environment variables di production
2. Install dependencies: `pip install -r requirements.txt`
3. Run dengan production server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment
```bash
cd meeting-summarizer
npm run build
```
Hasil build akan ada di folder `dist/`

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **API Keys Error**
   - Pastikan file `.env` sudah dibuat dengan API keys yang benar
   - Cek apakah API keys masih valid

2. **File Upload Error**
   - Pastikan file berformat MP3
   - Cek ukuran file (max 50MB)

3. **Download Error**
   - Pastikan task sudah selesai diproses
   - Cek apakah file masih ada di server

4. **CORS Error**
   - Pastikan backend dan frontend berjalan di port yang benar
   - Cek konfigurasi CORS di `main.py`

## 📞 Support

Jika ada masalah atau pertanyaan, silakan buat issue di repository ini.
