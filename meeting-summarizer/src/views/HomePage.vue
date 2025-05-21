<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1>Transform Your Meetings into Action Items</h1>
        <p>Upload your meeting recordings and get instant transcriptions and summaries powered by AI</p>
      </div>
    </div>
    
    <FileUpload />
    
    <div class="features-section">
      <h2>How It Works</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M2 12a5 5 0 0 0 5 5 8 8 0 0 1 5 2 8 8 0 0 1 5-2 5 5 0 0 0 5-5V7H2v5z"></path>
              <path d="M6 8v4"></path>
              <path d="M18 8v4"></path>
              <path d="M18 12h.01"></path>
              <path d="M6 12h.01"></path>
            </svg>
          </div>
          <h3>1. Upload Audio</h3>
          <p>Upload your MP3 audio file of the meeting or conversation</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3z"></path>
              <path d="M7 22V11"></path>
              <path d="M1 22V11"></path>
            </svg>
          </div>
          <h3>2. AI Processing</h3>
          <p>Our AI will transcribe and analyze the content</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3.01" y2="6"></line>
              <line x1="3" y1="12" x2="3.01" y2="12"></line>
              <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
          </div>
          <h3>3. Get Results</h3>
          <p>Receive a concise summary with key points and action items</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from "@/components/FileUpload.vue";

export default {
  components: {
    FileUpload
  }
};
</script>

<style scoped>
.home-container {
  background-color: #f5f7fa;
  padding-bottom: 4rem;
}

.hero-section {
  background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
  color: white;
  padding: 3rem 1rem;
  margin-bottom: 2rem;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero-content h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.hero-content p {
  font-size: 1.125rem;
  max-width: 600px;
  margin: 0 auto;
  opacity: 0.9;
}

.features-section {
  max-width: 1200px;
  margin: 4rem auto 0;
  padding: 0 1rem;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2rem;
  color: #2c3e50;
  position: relative;
}

.features-section h2:after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  width: 60px;
  height: 3px;
  background-color: #42b983;
  transform: translateX(-50%);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  background-color: rgba(66, 185, 131, 0.1);
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
  color: #42b983;
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: #34495e;
  font-size: 1.25rem;
  font-weight: 600;
}

.feature-card p {
  color: #6c757d;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .hero-content h1 {
    font-size: 2rem;
  }
  
  .hero-content p {
    font-size: 1rem;
  }
  
  .features-section h2 {
    font-size: 1.5rem;
  }
  
  .feature-icon {
    width: 60px;
    height: 60px;
  }
}
</style>