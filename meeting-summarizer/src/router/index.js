import { createRouter, createWebHistory } from 'vue-router';  // Menggunakan createRouter dan createWebHistory
import HomePage from "@/views/HomePage.vue";  // Komponen yang akan dirender

const routes = [
  {
    path: '/',
    name: 'HomePage',  // Nama komponen yang dituju
    component: HomePage,  // Menentukan komponen yang akan dirender
  },
];

const router = createRouter({
  history: createWebHistory(),  // Menggunakan history mode
  routes,  // Menentukan rute-rute yang ada
});

export default router;
