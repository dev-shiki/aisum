<template>
  <div id="app">
    <header>
      <h1>Transcribe & Summarize Audio</h1>
    </header>
    <main>
      <FileUpload />
    </main>
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
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

header {
  background-color: #42b983;
  padding: 20px;
}

h1 {
  font-size: 2rem;
  color: white;
}
</style>
