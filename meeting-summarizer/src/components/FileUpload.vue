<template>
    <div class="upload-container">
      <h2>Upload File MP3 untuk Ringkasan</h2>
      <input type="file" accept=".mp3" @change="handleFileUpload" />
  
      <!-- Loading Animation -->
      <div v-if="isUploading" class="loading-container">
        <img src="@/assets/loading-animation.gif" alt="Loading..." />
        <p>Proses sedang berjalan...</p>
      </div>
  
      <!-- Menampilkan Status Proses -->
      <div v-if="uploadStatus">
        <p>{{ uploadStatus.message }}</p>
        <div v-if="uploadStatus.status === 'completed'">
          <h3>Ringkasan:</h3>
          <p>{{ uploadStatus.summary }}</p>
          <!-- Link untuk Download File Ringkasan -->
          <a v-if="uploadStatus.summary_file" :href="uploadStatus.summary_file" download>Unduh Ringkasan</a>
        </div>
        <div v-if="uploadStatus.status === 'failed'">
          <p style="color: red;">Proses gagal: {{ uploadStatus.error }}</p>
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
    },
  };
  </script>
  
  <style scoped>
  .upload-container {
    text-align: center;
    margin: 50px auto;
    max-width: 600px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  
  input[type="file"] {
    padding: 10px;
    margin: 20px 0;
  }
  
  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }
  
  h2 {
    color: #333;
  }
  
  p {
    color: #555;
  }
  
  h3 {
    font-size: 1.2rem;
    margin-top: 20px;
  }
  
  img {
    width: 50px;
    height: 50px;
  }
  </style>
  