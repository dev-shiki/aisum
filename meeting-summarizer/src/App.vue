<template>
  <div id="app">
    <header class="app-header">
      <div class="header-content">
        <div class="logo-container">
          <h1>Meeting Summarizer</h1>
          <p class="tagline">Transcribe & Summarize Audio with AI</p>
        </div>
      </div>
    </header>
    
    <main class="main-content">
      <FileUpload />
    </main>
    
    <footer class="app-footer">
      <div class="footer-content">
        <p>&copy; 2024 Meeting Summarizer | Powered by AI</p>
      </div>
    </footer>
  </div>
</template>

<script>
import FileUpload from "@/components/FileUpload.vue";

export default {
  name: "App",
  components: {
    FileUpload,
  },
};
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  text-align: center;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #42b983 0%, #2c9a7a 100%);
  padding: 2rem 1rem;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo-container {
  text-align: center;
}

.logo-container h1 {
  font-size: 2.5rem;
  margin: 0;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.tagline {
  margin-top: 0.5rem;
  font-size: 1.125rem;
  opacity: 0.9;
  font-weight: 400;
}

.main-content {
  flex: 1;
  padding: 2rem 1rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: #2c3e50;
  color: white;
  padding: 1.5rem 1rem;
  margin-top: 2rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  font-size: 0.875rem;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .app-header {
    padding: 1.5rem 1rem;
  }
  
  .logo-container h1 {
    font-size: 2rem;
  }
  
  .tagline {
    font-size: 1rem;
  }
}
</style>
