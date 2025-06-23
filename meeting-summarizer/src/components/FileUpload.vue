<template>
  <div class="upload-container">
    <div class="card">
      <div class="card-header">
        <h2>Transcription & Summary</h2>
        <p class="subtitle">Upload audio files or YouTube links to get instant transcriptions and summaries</p>
      </div>
      
      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button 
          @click="activeTab = 'file'" 
          :class="{ 'active': activeTab === 'file' }"
          class="tab-btn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          Upload File
        </button>
        <button 
          @click="activeTab = 'youtube'" 
          :class="{ 'active': activeTab === 'youtube' }"
          class="tab-btn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"></path>
            <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"></polygon>
          </svg>
          YouTube Link
        </button>
      </div>
      
      <div class="upload-area" :class="{ 'is-uploading': isUploading }">
        <!-- File Upload Tab -->
        <div v-if="activeTab === 'file' && !isUploading && !uploadStatus" class="upload-prompt">
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

        <!-- YouTube Link Tab -->
        <div v-if="activeTab === 'youtube' && !isUploading && !uploadStatus" class="youtube-prompt">
          <div class="youtube-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"></path>
              <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"></polygon>
            </svg>
          </div>
          <div class="youtube-form">
            <input 
              v-model="youtubeUrl" 
              type="url" 
              placeholder="Paste YouTube URL here..."
              class="youtube-input"
              @keyup.enter="processYouTubeUrl"
            />
            <button 
              @click="processYouTubeUrl" 
              :disabled="!youtubeUrl || !isValidYouTubeUrl"
              class="youtube-btn"
            >
              Process Video
            </button>
          </div>
          <p class="youtube-hint">Paste any YouTube video URL to get transcription and summary</p>
        </div>

        <!-- Processing States -->
        <div v-if="isUploading" class="processing-state">
          <div class="loader"></div>
          <h3>{{ uploadStatus ? uploadStatus.message : 'Processing your content...' }}</h3>
          <p class="processing-details">This may take a few minutes depending on the content length</p>
          
          <!-- YouTube Progress Steps -->
          <div v-if="activeTab === 'youtube'" class="progress-steps">
            <div class="step" :class="{ 'active': processingStep >= 1, 'completed': processingStep > 1 }">
              <div class="step-icon">📥</div>
              <div class="step-text">Downloading YouTube Audio</div>
            </div>
            <div class="step" :class="{ 'active': processingStep >= 2, 'completed': processingStep > 2 }">
              <div class="step-icon">🎤</div>
              <div class="step-text">Transcribing Audio</div>
            </div>
            <div class="step" :class="{ 'active': processingStep >= 3, 'completed': processingStep > 3 }">
              <div class="step-icon">📝</div>
              <div class="step-text">Generating Summary</div>
            </div>
          </div>
        </div>

        <!-- Results Display -->
        <div v-if="uploadStatus && uploadStatus.status === 'completed'" class="results-container">
          <h3 class="results-header">Summary Complete!</h3>
          
          <!-- Processing Info untuk YouTube -->
          <div v-if="uploadStatus.processing_info" class="processing-info">
            <div class="info-item">
              <span class="info-label">Content Type:</span>
              <span class="info-value">{{ uploadStatus.processing_info.content_type }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Transcription:</span>
              <span class="info-value">{{ uploadStatus.processing_info.transcription_chars.toLocaleString() }} chars</span>
            </div>
            <div class="info-item">
              <span class="info-label">Summary:</span>
              <span class="info-value">{{ uploadStatus.processing_info.summary_chars.toLocaleString() }} chars</span>
            </div>
            <div class="info-item">
              <span class="info-label">Compression:</span>
              <span class="info-value">{{ uploadStatus.processing_info.compression_ratio }}</span>
            </div>
          </div>
          
          <div class="results-box">
            <h4>Summary</h4>
            <div class="summary-content">
              <template v-if="isJson(summaryData)">
                <div v-if="summaryData.executive_summary">
                  <h5>Executive Summary</h5>
                  <p>{{ summaryData.executive_summary }}</p>
                </div>
                <div v-if="summaryData.key_points && summaryData.key_points.length">
                  <h5>Key Points</h5>
                  <ul>
                    <li v-for="(point, idx) in summaryData.key_points" :key="idx">
                      <b>{{ point.point || point.topic }}:</b> {{ point.description || point.summary }}
                    </li>
                  </ul>
                </div>
                <div v-if="summaryData.tutorial_steps && summaryData.tutorial_steps.length">
                  <h5>Tutorial Steps</h5>
                  <ul>
                    <li v-for="(step, idx) in summaryData.tutorial_steps" :key="idx">
                      <b>{{ step.step }}:</b> {{ step.description }} <span v-if="step.tips">({{ step.tips }})</span>
                    </li>
                  </ul>
                </div>
                <div v-if="summaryData.tips_and_tricks && summaryData.tips_and_tricks.length">
                  <h5>Tips & Tricks</h5>
                  <ul>
                    <li v-for="(tip, idx) in summaryData.tips_and_tricks" :key="idx">{{ tip }}</li>
                  </ul>
                </div>
                <div v-if="summaryData.recommendations && summaryData.recommendations.length">
                  <h5>Recommendations</h5>
                  <ul>
                    <li v-for="(rec, idx) in summaryData.recommendations" :key="idx">{{ rec }}</li>
                  </ul>
                </div>
                <div v-if="summaryData.call_to_action">
                  <h5>Call to Action</h5>
                  <p>{{ summaryData.call_to_action }}</p>
                </div>
                <div v-if="summaryData.related_content && summaryData.related_content.length">
                  <h5>Related Content</h5>
                  <ul>
                    <li v-for="(rel, idx) in summaryData.related_content" :key="idx">{{ rel }}</li>
                  </ul>
                </div>
                <div v-if="summaryData.products_mentioned && summaryData.products_mentioned.length">
                  <h5>Products Mentioned</h5>
                  <ul>
                    <li v-for="(prod, idx) in summaryData.products_mentioned" :key="idx">
                      <b>{{ prod.product }}:</b> {{ prod.description }} <span v-if="prod.opinion">({{ prod.opinion }})</span>
                    </li>
                  </ul>
                </div>
              </template>
              <template v-else>
                <p>{{ uploadStatus.summary }}</p>
              </template>
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
          
          <button @click="resetForm" class="reset-btn">Process Another Content</button>
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
          <span>Support for MP3 files and YouTube links</span>
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
      youtubeUrl: '',
      activeTab: 'file',
      isUploading: false,
      uploadStatus: null,
      retryCount: 0,
      isDownloading: false,
      processingStep: 0,
    };
  },
  computed: {
    isValidYouTubeUrl() {
      const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
      return youtubeRegex.test(this.youtubeUrl);
    },
    summaryData() {
      // Try to parse summary as JSON if possible
      try {
        if (typeof this.uploadStatus.summary === 'string') {
          return JSON.parse(this.uploadStatus.summary);
        }
        return this.uploadStatus.summary;
      } catch {
        return this.uploadStatus.summary;
      }
    }
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (file && (file.type === "audio/mp3" || file.type === "audio/mpeg")) {
        this.file = file;
        this.uploadFile();
      } else {
        alert("Hanya file MP3 yang didukung.");
      }
    },

    async processYouTubeUrl() {
      if (!this.isValidYouTubeUrl) {
        alert("Masukkan URL YouTube yang valid.");
        return;
      }

      this.isUploading = true;
      this.uploadStatus = null;
      this.processingStep = 1; // Mulai dengan step 1: Download

      try {
        // Progress steps dengan timing yang lebih realistis
        setTimeout(() => {
          this.processingStep = 2; // Transcribe (2-5 detik)
          this.uploadStatus = { status: "processing", message: "Transcribing audio..." };
        }, 3000);
        
        setTimeout(() => {
          this.processingStep = 3; // Summarize (bisa 10-30 detik)
          this.uploadStatus = { status: "processing", message: "Generating AI summary (this may take 10-30 seconds)..." };
        }, 8000);
        
        const response = await this.$axios.post("/api/summarize/youtube/", {
          youtube_url: this.youtubeUrl
        }, {
          timeout: 600000 // 10 menit
        });

        this.isUploading = false;
        this.processingStep = 4; // Completed
        this.uploadStatus = {
          status: "completed",
          message: "Ringkasan selesai!",
          summary: response.data.summary || "Ringkasan tidak ditemukan.",
          content_type: response.data.content_type,
          transcription_length: response.data.transcription_length,
          processing_info: response.data.processing_info
        };
      } catch (error) {
        this.isUploading = false;
        this.processingStep = 0;
        console.error("YouTube processing failed:", error);
        
        let errorMessage = "Terjadi kesalahan saat memproses video YouTube.";
        
        if (error.code === 'ECONNABORTED') {
          errorMessage = "Request timeout - video terlalu panjang atau koneksi lambat.";
        } else if (error.response?.status === 400) {
          errorMessage = error.response.data.detail || "URL YouTube tidak valid atau video tidak dapat diakses.";
        } else if (error.response?.status === 500) {
          errorMessage = error.response.data.detail || "Server error - coba lagi nanti.";
        } else if (error.message.includes('Network Error')) {
          errorMessage = "Koneksi ke server terputus. Pastikan backend server berjalan.";
        }
        
        this.uploadStatus = {
          status: "failed",
          message: errorMessage,
          error: error.response?.data?.detail || error.message,
        };
      }
    },

    async uploadFile() {
      const formData = new FormData();
      formData.append("file", this.file);

      this.isUploading = true;
      this.uploadStatus = null;
      this.retryCount = 0;

      try {
        const response = await this.$axios.post("/api/summarize/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

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
          const statusResponse = await this.$axios.get(`/api/summarize/status/${taskId}`);
          const status = statusResponse.data;

          if (status.status === "completed") {
            clearInterval(interval);
            this.isUploading = false;
            this.uploadStatus = {
              status: "completed",
              message: "Ringkasan selesai!",
              summary: status.summary || "Ringkasan tidak ditemukan.",
              summary_file: status.summary_file || null,
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
      }, 3000);
    },
    
    resetForm() {
      this.file = null;
      this.youtubeUrl = '';
      this.uploadStatus = null;
      this.isUploading = false;
      this.isDownloading = false;
      this.processingStep = 0;
    },

    async downloadSummary() {
      if (!this.uploadStatus || !this.uploadStatus.summary) {
        alert("Tidak ada ringkasan untuk diunduh.");
        return;
      }

      this.isDownloading = true;

      try {
        // Create a blob and download
        const blob = new Blob([this.uploadStatus.summary], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `summary_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Download failed:", error);
        alert("Gagal mengunduh ringkasan.");
      } finally {
        this.isDownloading = false;
      }
    },

    isJson(val) {
      return val && typeof val === 'object' && !Array.isArray(val);
    },
  },
};
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.tab-btn {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.tab-btn.active {
  background: white;
  color: #667eea;
  border-bottom: 2px solid #667eea;
}

.tab-btn svg {
  width: 18px;
  height: 18px;
}

/* Upload Area */
.upload-area {
  padding: 40px;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-prompt, .youtube-prompt {
  text-align: center;
  max-width: 400px;
}

.upload-icon, .youtube-icon {
  margin-bottom: 20px;
  color: #667eea;
}

.upload-label {
  display: inline-block;
  padding: 15px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-bottom: 15px;
}

.upload-label:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.file-input {
  display: none;
}

.upload-hint, .youtube-hint {
  color: #6c757d;
  font-size: 14px;
  margin: 0;
}

/* YouTube Form */
.youtube-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.youtube-input {
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.youtube-input:focus {
  outline: none;
  border-color: #667eea;
}

.youtube-btn {
  padding: 15px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.youtube-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.youtube-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Processing State */
.processing-state {
  text-align: center;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.processing-state h3 {
  margin: 0 0 10px 0;
  color: #495057;
}

.processing-details {
  color: #6c757d;
  margin: 0;
}

/* YouTube Progress Steps */
.progress-steps {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.step {
  text-align: center;
  flex: 1;
  position: relative;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 12px;
  right: -50%;
  width: 100%;
  height: 2px;
  background: #e9ecef;
  z-index: 1;
}

.step.active {
  opacity: 1;
  color: #667eea;
  transform: scale(1.1);
}

.step.completed {
  opacity: 1;
  color: #28a745;
}

.step.completed:not(:last-child)::after {
  background: #28a745;
}

.step-icon {
  font-size: 24px;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
  background: white;
  width: 24px;
  height: 24px;
  margin-left: auto;
  margin-right: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-text {
  color: #6c757d;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.step.active .step-text {
  color: #667eea;
}

.step.completed .step-text {
  color: #28a745;
}

/* Results */
.results-container {
  text-align: center;
  max-width: 600px;
}

.results-header {
  color: #28a745;
  margin-bottom: 20px;
}

.results-box {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: left;
}

.results-box h4 {
  margin: 0 0 15px 0;
  color: #495057;
}

.summary-content {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  margin-bottom: 15px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.6;
}

.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.download-btn:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
}

.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.download-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.reset-btn {
  padding: 12px 24px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Error */
.error-container {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  color: #dc3545;
  margin-bottom: 20px;
}

.error-container h3 {
  color: #dc3545;
  margin-bottom: 15px;
}

.error-message {
  color: #6c757d;
  margin-bottom: 20px;
}

.retry-btn {
  padding: 12px 24px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #c82333;
  transform: translateY(-1px);
}

/* Features */
.features-list {
  background: #f8f9fa;
  padding: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #495057;
}

.feature-icon {
  color: #28a745;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .upload-container {
    padding: 10px;
  }
  
  .card-header {
    padding: 20px;
  }
  
  .card-header h2 {
    font-size: 24px;
  }
  
  .upload-area {
    padding: 20px;
  }
  
  .tab-btn {
    padding: 12px 15px;
    font-size: 13px;
  }
  
  .features-list {
    grid-template-columns: 1fr;
    padding: 20px;
  }
}

/* Processing Info */
.processing-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.info-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #495057;
}

.info-item:first-child .info-value {
  color: #667eea;
}

.info-item:nth-child(2) .info-value {
  color: #28a745;
}

.info-item:nth-child(3) .info-value {
  color: #fd7e14;
}

.info-item:last-child .info-value {
  color: #dc3545;
}
</style>
