import { createStore } from "vuex";  // Gunakan createStore untuk Vuex di Vue 3

export default createStore({
  state: {
    uploadStatus: null, // Status upload atau status lainnya
  },
  mutations: {
    setUploadStatus(state, status) {
      state.uploadStatus = status; // Mutasi untuk mengubah status
    },
  },
  actions: {
    updateUploadStatus({ commit }, status) {
      commit("setUploadStatus", status); // Menjalankan mutasi untuk mengubah status
    },
  },
});
