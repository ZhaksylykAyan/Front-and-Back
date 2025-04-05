<template>
  <div v-if="initialized">
    <Header v-if="showHeader" />
    <router-view />
  </div>
</template>

<script setup>
import Header from "./pages/Header.vue";
import { useRoute } from "vue-router";
import { computed, ref, onMounted } from "vue";
import { useAuthStore } from "./store/auth";

const route = useRoute();
const showHeader = computed(
  () => !["/login", "/register", "/forgot-password"].includes(route.path)
);

const authStore = useAuthStore();
const initialized = ref(false);

// Only try to restore user/token on protected pages
onMounted(async () => {
  const publicPages = ["/login", "/register", "/forgot-password"];
  if (!publicPages.includes(route.path) && !authStore.isLoggingIn) {
    await authStore.restoreUser();
  }
  initialized.value = true;
});
</script>
