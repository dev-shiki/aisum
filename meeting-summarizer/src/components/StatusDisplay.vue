<template>
    <div v-if="status">
      <p>Status: {{ status }}</p>
      <p v-if="message">{{ message }}</p>
      <div v-if="isLoading">
        <img src="@/assets/loading-animation.gif" alt="loading" />
        <p>Loading...</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      status: String,
      message: String,
      isLoading: Boolean
    }
  };
  </script>
  