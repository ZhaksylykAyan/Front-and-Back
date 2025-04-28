<template>
  <div v-if="initialized">
    <Header v-if="showHeader" />
    <router-view />
    <ChatModal v-if="chatStore.isModalOpen" />
  </div>
</template>

<script setup>
import Header from "./pages/Header.vue";
import ChatModal from "./components/Chat/ChatModal.vue"; // 👈 добавляем
import { useRoute } from "vue-router";
import { computed, ref, onMounted } from "vue";
import { useAuthStore } from "./store/auth";
import { useChatStore } from "./store/chat"; // 👈 подключаем chat store

const route = useRoute();
const authStore = useAuthStore();
const chatStore = useChatStore(); // 👈 нужно для v-if модалки
const initialized = ref(false);

const showHeader = computed(() =>
  !["/login", "/register", "/forgot-password"].includes(route.path)
);

// Восстановление пользователя при загрузке
onMounted(async () => {
  const publicPages = ["/login", "/register", "/forgot-password"];
  if (!publicPages.includes(route.path) && !authStore.isLoggingIn) {
    await authStore.restoreUser();
  }
  initialized.value = true;
});
</script>
