<template>
  <div class="status-container" v-if="status">
    <div class="status-card" :class="statusClass">
      <div class="status-icon">
        <!-- Processing Icon -->
        <svg v-if="status === 'processing'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        
        <!-- Success Icon -->
        <svg v-else-if="status === 'completed'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        
        <!-- Error Icon -->
        <svg v-else-if="status === 'failed'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        
        <!-- Default Icon -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
      </div>
      
      <div class="status-content">
        <h3 class="status-title">{{ statusTitle }}</h3>
        <p v-if="message" class="status-message">{{ message }}</p>
        
        <div v-if="isLoading" class="loader-container">
          <div class="loader"></div>
          <p class="loading-text">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    status: String,
    message: String,
    isLoading: Boolean
  },
  computed: {
    statusClass() {
      if (!this.status) return '';
      
      switch (this.status) {
        case 'processing':
          return 'status-processing';
        case 'completed':
          return 'status-success';
        case 'failed':
          return 'status-error';
        default:
          return '';
      }
    },
    statusTitle() {
      if (!this.status) return '';
      
      switch (this.status) {
        case 'processing':
          return 'Processing...';
        case 'completed':
          return 'Completed Successfully';
        case 'failed':
          return 'Processing Failed';
        default:
          return this.status.charAt(0).toUpperCase() + this.status.slice(1);
      }
    },
    loadingMessage() {
      return this.message || 'Your request is being processed. This may take a few minutes...';
    }
  }
};
</script>

<style scoped>
.status-container {
  margin: 1.5rem 0;
}

.status-card {
  display: flex;
  align-items: center;
  padding: 1.25rem;
  border-radius: 8px;
  background-color: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.status-processing {
  background-color: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.status-success {
  background-color: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.status-error {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
}

.status-icon {
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-processing .status-icon {
  color: #2196f3;
}

.status-success .status-icon {
  color: #4caf50;
}

.status-error .status-icon {
  color: #f44336;
}

.status-content {
  flex: 1;
}

.status-title {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.status-message {
  margin: 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.loader-container {
  display: flex;
  align-items: center;
  margin-top: 0.75rem;
}

.loader {
  width: 16px;
  height: 16px;
  border: 2px solid #e0e0e0;
  border-top: 2px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.75rem;
}

.loading-text {
  margin: 0;
  font-size: 0.875rem;
  color: #6c757d;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .status-card {
    flex-direction: column;
    text-align: center;
  }
  
  .status-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .loader-container {
    justify-content: center;
  }
}
</style>