<template>
  <div class="home-container">
    <FileUpload />
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
  background-color: #f9f9f9;
  padding: 50px;
  text-align: center;
}
</style>
