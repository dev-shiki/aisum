[![codecov](https://codecov.io/gh/dev-shiki/aisum/graph/badge.svg?token=EXGPRQ7C44)](https://codecov.io/gh/dev-shiki/aisum)

# Meeting Summarizer

Meeting Summarizer is a web application that allows users to upload meeting audio files or YouTube links and receive automatic transcriptions and narrative summaries using state-of-the-art AI models.

## 🚀 Features

- **Audio & YouTube Transcription**: Convert meeting audio (MP3) or YouTube videos to text using Whisper (via Groq API)
- **AI Summarization**: Generate concise, narrative summaries using Gemini (Google API)
- **Real-time Status**: Track processing status in real time
- **Downloadable Results**: Download summaries as text files
- **User-friendly Interface**: Responsive and modern Vue.js frontend
- **Robust Error Handling**: Comprehensive error and status reporting

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python)
- Whisper API (Groq)
- Gemini API (Google)
- yt-dlp (YouTube audio download)
- Uvicorn (ASGI server)
- python-dotenv (env management)

**Frontend**
- Vue.js 3
- Axios
- Vue Router
- Vuex
- CSS3

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- API keys for Groq (Whisper) and Google Gemini

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd app
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Activate the virtual environment:
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env and add your API keys
```

### 3. Frontend Setup
```bash
cd ../meeting-summarizer
npm install
```

## 🚀 Running the Application

### 1. Start the Backend Server
```bash
cd backend
# Development mode (auto-reload):
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Production mode:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Backend runs at: http://localhost:8000

### 2. Start the Frontend Development Server
```bash
cd ../meeting-summarizer
npm run serve
```
Frontend runs at: http://localhost:5173

### 3. Build for Production
```bash
npm run build
```

## 🔒 Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# API Configuration
WHISPER_API_URL=https://api.groq.com/openai/v1/audio/transcriptions
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent

# API Keys (Required)
WHISPER_API_KEY=your_whisper_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
TEMP_FOLDER=temp/
MAX_SUMMARY_LENGTH=200

# Gemini Rate Limit (optional)
GEMINI_RPM=15
GEMINI_TPM=1000000
GEMINI_RPD=200

# Server Configuration
PORT=8000
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
app/
├── backend/
│   ├── app/
│   │   ├── config.py           # Configuration
│   │   ├── main.py             # FastAPI entrypoint
│   │   ├── routes/
│   │   │   └── summarize.py    # API endpoints
│   │   ├── services/
│   │   │   ├── whisper.py      # Whisper API integration
│   │   │   ├── gemini.py       # Gemini API integration
│   │   │   └── llama.py        # (Optional) Llama API integration
│   │   └── utils/
│   │       └── logger.py       # Logging utilities
│   ├── temp/                   # Temporary files
│   ├── requirements.txt        # Python dependencies
│   └── env.example             # Environment variable template
└── meeting-summarizer/
    ├── src/
    │   ├── components/         # Vue components
    │   ├── assets/             # Static assets
    │   ├── App.vue             # Root component
    │   └── main.js             # Vue entrypoint
    ├── package.json            # Node.js dependencies
    └── README.md               # Frontend docs
```

## 🔌 API Endpoints

### POST `/api/summarize/`
Upload an MP3 file for processing.
- **Request**: Multipart form data with an MP3 file
- **Response**: `{ "task_id": "uuid", "status": "processing" }`

### POST `/api/summarize/youtube/`
Submit a YouTube link for processing.
- **Request**: `{ "youtube_url": "<url>" }`
- **Response**: Summary result or error

### GET `/api/summarize/status/{task_id}`
Check processing status.
- **Response**: Task status (processing/completed/failed)

### GET `/api/summarize/download/{task_id}`
Download the summary file.
- **Response**: TXT file

### DELETE `/api/summarize/cleanup/{task_id}`
Delete files and task data.
- **Response**: Cleanup confirmation

### GET `/api/health`
Health check endpoint.

## 🧪 Testing

### Backend
```bash
cd backend
# (Add tests with pytest as needed)
```

### Frontend
```bash
cd meeting-summarizer
npm run lint
```

## 🆘 Troubleshooting

- **API Key Errors**: Ensure `.env` is set up with valid API keys.
- **File Upload Errors**: Only MP3 files are supported. Max size: 50MB.
- **YouTube Download Errors**: Ensure the link is valid and the video is accessible.
- **CORS Issues**: Make sure backend and frontend are running on the correct ports. Check CORS settings in `main.py`.
- **Other Issues**: Check logs for detailed error messages.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🚢 Docker & GCP Deployment

### Local Development with Docker Compose

```bash
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Build and Push Images for GCP

1. **Build Docker images:**
   ```bash
   docker build -t gcr.io/<your-gcp-project-id>/aisum-backend:latest ./backend
   docker build -t gcr.io/<your-gcp-project-id>/aisum-frontend:latest ./meeting-summarizer
   ```
2. **Push to Google Container Registry:**
   ```bash
   docker push gcr.io/<your-gcp-project-id>/aisum-backend:latest
   docker push gcr.io/<your-gcp-project-id>/aisum-frontend:latest
   ```
3. **Deploy using GCP Cloud Run, GKE, or Compute Engine as needed.**

- Make sure to set up your `.env` file for the backend and configure environment variables in your GCP deployment.
- For persistent storage (e.g., `/app/app/temp`), use GCP volumes or buckets as appropriate.

---
