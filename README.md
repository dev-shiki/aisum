# Meeting Summarizer

Aplikasi yang memungkinkan pengguna untuk mengunggah rekaman audio rapat dan mendapatkan transkripsi serta ringkasan otomatis menggunakan teknologi AI.

## 📋 Deskripsi

Meeting Summarizer adalah aplikasi berbasis web yang membantu mengotomatisasi proses notulensi rapat. Aplikasi ini menggunakan model Whisper dari OpenAI untuk transkripsi audio dan model Llama untuk ringkasan teks, melalui API Groq.

## ✨ Fitur

- Unggah file audio MP3 rapat
- Transkripsi otomatis menggunakan Whisper
- Ringkasan otomatis menggunakan model AI Llama
- Tampilan status proses secara real-time
- Unduh hasil ringkasan dalam format teks

## 🛠️ Teknologi

### Backend
- **FastAPI**: Framework Python untuk RESTful API
- **Whisper API**: Untuk transkripsi audio ke teks
- **Llama API**: Untuk ringkasan teks dengan AI
- **Asyncio**: Untuk pemrosesan asinkronus

### Frontend
- **Vue.js 3**: Frontend framework
- **Axios**: Untuk HTTP requests
- **Vue Router**: Untuk navigasi
- **Vuex**: Untuk state management

## 🚀 Instalasi dan Penggunaan

### Prasyarat
- Python 3.8+
- Node.js dan npm
- API key Groq

### Langkah Instalasi Backend

1. Clone repository
```bash
git clone https://github.com/username/meeting-summarizer.git
cd meeting-summarizer/backend
```

2. Buat dan aktifkan virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Untuk Linux/Mac
venv\Scripts\activate     # Untuk Windows
```

3. Install dependensi
```bash
pip install -r requirements.txt
```

4. Setup file `.env` dengan API key
```
WHISPER_API_KEY="your_groq_api_key"
LLAMA_API_KEY="your_groq_api_key"
```

5. Jalankan server backend
```bash
python -m app.main
```

### Langkah Instalasi Frontend

1. Pindah ke direktori frontend
```bash
cd ../meeting-summarizer
```

2. Install dependensi
```bash
npm install
```

3. Jalankan server development
```bash
npm run serve
```

4. Buka browser dan akses `http://localhost:5173`

## 🧩 Struktur Proyek

```
meeting-summarizer/
├── backend/
│   ├── app/
│   │   ├── config.py         # Konfigurasi API
│   │   ├── main.py           # Entry point aplikasi
│   │   ├── routes/           # Definisi endpoint API
│   │   ├── services/         # Logic pemrosesan (whisper, llama)
│   │   └── utils/            # Utilitas (logger, dll)
│   └── .env                  # File environment variables
│
└── src/
    ├── App.vue               # Komponen utama Vue
    ├── assets/               # Asset statis (gambar, css)
    ├── components/           # Komponen Vue reusable
    ├── main.js               # Entry point frontend
    ├── router/               # Konfigurasi routing
    ├── store/                # State management
    └── views/                # Halaman Vue
```

## 📝 Cara Penggunaan

1. Buka aplikasi melalui browser
2. Klik tombol unggah dan pilih file MP3 rekaman rapat
3. Tunggu proses transkripsi dan ringkasan selesai
4. Lihat dan unduh hasil ringkasan rapat

## 🔒 Keamanan

- API key disimpan di server backend dan tidak pernah diekspos ke frontend
- File audio dihapus otomatis setelah pemrosesan selesai
- Koneksi API menggunakan HTTPS

## 🤝 Kontribusi

Silakan berkontribusi pada proyek ini dengan membuat pull request atau melaporkan bug melalui issues.

## 👏 Penghargaan

- OpenAI untuk model Whisper
- Groq untuk API yang cepat dan mudah digunakan
- Tim FastAPI dan Vue.js atas framework luar biasa

---
