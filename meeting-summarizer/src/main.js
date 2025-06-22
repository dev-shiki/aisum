import axios from "axios";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";  // Opsional, jika Anda menggunakan Vuex
import './assets/css/global-styles.css';

const app = createApp(App);
app.config.globalProperties.$axios = axios;  // Menambahkan axios ke dalam global properties
axios.defaults.baseURL = "http://localhost:8000/api";  // Pastikan URL API backend sudah benar
app.use(router);
app.use(store);
app.mount("#app");
