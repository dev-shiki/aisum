<template>
  <div class="upload-container">
    <div class="card">
      <div class="card-header">
        <h2>Upload Audio File for Transcription & Summary</h2>
        <p class="subtitle">Upload your meeting recordings and get instant transcriptions and summaries</p>
      </div>
      
      <div class="upload-area" :class="{ 'is-uploading': isUploading }">
        <div v-if="!isUploading && !uploadStatus" class="upload-prompt">
          <div class="upload-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
          </div>
          <label for="file-upload" class="upload-label">
            <span>Choose MP3 File</span> or drag and drop
            <input 
              id="file-upload" 
              type="file" 
              accept=".mp3" 
              @change="handleFileUpload" 
              class="file-input"
            />
          </label>
          <p class="upload-hint">Only MP3 files are supported</p>
        </div>

        <!-- Processing States -->
        <div v-if="isUploading" class="processing-state">
          <div class="loader"></div>
          <h3>{{ uploadStatus ? uploadStatus.message : 'Processing your audio...' }}</h3>
          <p class="processing-details">This may take a few minutes depending on the file size</p>
        </div>

        <!-- Results Display -->
        <div v-if="uploadStatus && uploadStatus.status === 'completed'" class="results-container">
          <h3 class="results-header">Summary Complete!</h3>
          
          <div class="results-box">
            <h4>Summary</h4>
            <div class="summary-content">
              <p>{{ uploadStatus.summary }}</p>
            </div>
            <button 
              @click="downloadSummary" 
              class="download-btn"
              :disabled="isDownloading"
            >
              <svg v-if="!isDownloading" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <div v-else class="download-spinner"></div>
              {{ isDownloading ? 'Downloading...' : 'Download Summary' }}
            </button>
          </div>
          
          <button @click="resetForm" class="reset-btn">Process Another File</button>
        </div>

        <!-- Error Display -->
        <div v-if="uploadStatus && uploadStatus.status === 'failed'" class="error-container">
          <div class="error-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <h3>Processing Failed</h3>
          <p class="error-message">{{ uploadStatus.error || 'An unknown error occurred' }}</p>
          <button @click="resetForm" class="retry-btn">Try Again</button>
        </div>
      </div>
      
      <div class="features-list">
        <div class="feature">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <span>High quality AI transcription</span>
        </div>
        <div class="feature">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <span>Concise and accurate summaries</span>
        </div>
        <div class="feature">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <span>Downloadable text files</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      isUploading: false,
      uploadStatus: null,
      retryCount: 0, // Menghitung jumlah percobaan ulang
      isDownloading: false,
    };
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      // Periksa apakah file memiliki tipe "audio/mp3" atau "audio/mpeg"
      if (file && (file.type === "audio/mp3" || file.type === "audio/mpeg")) {
        this.file = file;
        this.uploadFile();
      } else {
        alert("Hanya file MP3 yang didukung.");
      }
    },

    async uploadFile() {
      const formData = new FormData();
      formData.append("file", this.file);

      this.isUploading = true;
      this.uploadStatus = null;
      this.retryCount = 0; // Reset retry count

      try {
        // Kirim file ke backend untuk diproses
        const response = await this.$axios.post("/summarize/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        // Memeriksa status berdasarkan task_id
        this.checkStatus(response.data.task_id);
      } catch (error) {
        this.isUploading = false;
        console.error("Upload failed:", error);
        this.uploadStatus = {
          status: "failed",
          message: "Terjadi kesalahan saat mengunggah file.",
          error: error.message,
        };
      }
    },

    async checkStatus(taskId) {
      const interval = setInterval(async () => {
        try {
          const statusResponse = await this.$axios.get(`/summarize/status/${taskId}`);
          const status = statusResponse.data;

          if (status.status === "completed") {
            clearInterval(interval);
            this.isUploading = false;
            this.uploadStatus = {
              status: "completed",
              message: "Ringkasan selesai!",
              summary: status.summary || "Ringkasan tidak ditemukan.",
              summary_file: status.summary_file || null,  // Menambahkan file unduhan
            };
          } else if (status.status === "failed") {
            clearInterval(interval);
            this.isUploading = false;
            this.uploadStatus = {
              status: "failed",
              message: "Proses gagal, coba lagi nanti.",
              error: status.error || "Unknown error",
            };
          } else {
            this.uploadStatus = { status: status.status, message: status.message };
          }
        } catch (error) {
          clearInterval(interval);
          this.isUploading = false;
          console.error("Error fetching status:", error);
          this.uploadStatus = {
            status: "failed",
            message: "Terjadi kesalahan saat memeriksa status.",
            error: error.message,
          };
        }
      }, 3000); // Mengecek status setiap 3 detik
    },
    
    resetForm() {
      this.file = null;
      this.isUploading = false;
      this.uploadStatus = null;
      this.retryCount = 0;
      this.isDownloading = false;
      
      // Reset file input by recreating it
      const fileInput = document.getElementById('file-upload');
      if (fileInput) {
        fileInput.value = '';
      }
    },

    async downloadSummary() {
      this.isDownloading = true;
      try {
        // Gunakan task_id untuk download
        const taskId = this.uploadStatus.task_id;
        if (!taskId) {
          throw new Error("Task ID tidak ditemukan");
        }
        
        const response = await this.$axios.get(`/summarize/download/${taskId}`, {
          responseType: 'blob'
        });
        
        // Buat blob dan download
        const blob = new Blob([response.data], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `summary_${taskId}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        this.isDownloading = false;
      } catch (error) {
        this.isDownloading = false;
        console.error("Error downloading summary:", error);
        alert("Gagal mengunduh file ringkasan. Silakan coba lagi.");
      }
    },
  },
};
</script>

<style scoped>
.upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  min-height: 80vh;
}

.card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 800px;
  overflow: hidden;
}

.card-header {
  padding: 2rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaecef;
}

.card-header h2 {
  margin: 0;
  color: #343a40;
  font-size: 1.5rem;
  font-weight: 600;
}

.subtitle {
  color: #6c757d;
  margin-top: 0.5rem;
  font-size: 0.95rem;
}

.upload-area {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 300px;
  transition: all 0.3s ease;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.upload-icon {
  color: #42b983;
  margin-bottom: 1rem;
}

.upload-label {
  cursor: pointer;
  padding: 1rem 2rem;
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  text-align: center;
  width: 100%;
  max-width: 400px;
  transition: all 0.2s ease;
  color: #495057;
  font-weight: 500;
}

.upload-label:hover {
  border-color: #42b983;
  background-color: rgba(66, 185, 131, 0.05);
  color: #42b983;
}

.upload-label span {
  color: #42b983;
  font-weight: 600;
}

.file-input {
  display: none;
}

.upload-hint {
  margin-top: 0.75rem;
  color: #868e96;
  font-size: 0.875rem;
}

/* Processing State */
.processing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  text-align: center;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.processing-details {
  color: #868e96;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* Results Container */
.results-container {
  width: 100%;
  text-align: center;
}

.results-header {
  color: #42b983;
  margin-bottom: 1.5rem;
}

.results-box {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: left;
}

.results-box h4 {
  margin-top: 0;
  color: #343a40;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}

.summary-content {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.summary-content p {
  margin: 0;
  line-height: 1.6;
  color: #495057;
}

.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #42b983;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.download-btn:hover:not(:disabled) {
  background-color: #3aa876;
}

.download-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

.download-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.reset-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.reset-btn:hover {
  background-color: #5a6268;
}

/* Error Container */
.error-container {
  width: 100%;
  text-align: center;
}

.error-icon {
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.retry-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background-color: #c82333;
}

/* Features List */
.features-list {
  padding: 1.5rem 2rem;
  background-color: #f8f9fa;
  border-top: 1px solid #eaecef;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: 1.5rem;
}

.feature-icon {
  color: #42b983;
}

/* Responsive styles */
@media (max-width: 768px) {
  .upload-container {
    padding: 1rem;
  }
  
  .card-header {
    padding: 1.5rem;
  }
  
  .upload-area {
    padding: 1.5rem;
  }
  
  .features-list {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .feature {
    margin-right: 0;
  }
}
</style>
