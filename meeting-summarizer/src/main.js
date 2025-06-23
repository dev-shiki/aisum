import axios from "axios";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";  // Opsional, jika Anda menggunakan Vuex
import './assets/css/global-styles.css';

const app = createApp(App);

// Konfigurasi axios
axios.defaults.baseURL = "http://localhost:8000";
axios.defaults.timeout = 600000; // 10 menit timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Interceptor untuk error handling
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('Axios Error:', error);
    return Promise.reject(error);
  }
);

app.config.globalProperties.$axios = axios;
app.use(router);
app.use(store);
app.mount("#app");
