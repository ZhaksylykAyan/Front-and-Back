<template>
  <div class="auth-container">
    <div class="auth-box">
      <img src="../assets/logo.png" alt="Diplomatch Logo" class="logo" />
      <p class="tagline"><strong>Match. Collaborate. Graduate.</strong></p>
      <h2>Login</h2>

      <form @submit.prevent="handleLogin">
        <input type="email" v-model="email" placeholder="E-mail" required />
        <input
          type="password"
          v-model="password"
          placeholder="Password"
          required
        />
        <button type="submit" class="btn" :disabled="loading || isBlocked">
          {{ isBlocked ? `Please wait...` : "Login" }}
        </button>
      </form>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <router-link to="/forgot-password" class="switch-link">
        Forgot password?
      </router-link>
      <router-link to="/register" class="switch-link">
        Don't have an account? Register
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";

const email = ref("");
const password = ref("");
const errorMessage = ref("");
const loading = ref(false);
const isBlocked = ref(false);
const unblockTimeout = ref<number | null>(null);

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  if (loading.value || isBlocked.value) return;
  loading.value = true;
  errorMessage.value = "";

  try {
    const result = await authStore.login(email.value, password.value);
    if (result.success) {
      router.push("/dashboard");
    }
  } catch (error: any) {
    console.error("Login error:", error);

    if (error.blocked) {
      isBlocked.value = true;

      if (error.blockedUntil) {
        const until = new Date(error.blockedUntil);
        const localTime = until.toLocaleTimeString();
        errorMessage.value = `${error.message} (Try again at ${localTime})`;

        // Подсчёт времени до разблокировки
        const now = new Date();
        const waitMs = until.getTime() - now.getTime();

        if (waitMs > 0) {
          if (unblockTimeout.value) clearTimeout(unblockTimeout.value);
          unblockTimeout.value = window.setTimeout(() => {
            isBlocked.value = false;
            errorMessage.value = "";
          }, waitMs);
        }
      } else {
        errorMessage.value = error.message;
      }
    } else {
      errorMessage.value = error.message || "Login failed";
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* === General Styles === */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Inter", sans-serif;
}

body {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f3f4f6;
}

/* === Authentication Container === */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
}

.tagline {
  font-size: 1rem;
  color: #000000;
  margin-bottom: 1.5rem;
}

.auth-box {
  background: white;
  padding: 40px;
  width: 400px;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba( 0, 0, 0, 0.1);
  text-align: center;
}

.auth-box img {
  width: 150px;
  margin-bottom: 20px;
}

.auth-box h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #144a77;
}

/* === Input Fields === */
.auth-box input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  font-size: 16px;
}

/* === Buttons === */
.auth-box .btn {
  width: 100%;
  padding: 12px;
  background: #1e40af;
  color: white;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.auth-box .btn:disabled {
  background: #6b7280;
  cursor: not-allowed;
}

.auth-box .btn:hover:not(:disabled) {
  background: #1e3a8a;
}

/* === Links === */
.switch-link {
  display: block;
  margin-top: 15px;
  color: #1e40af;
  font-size: 14px;
  text-decoration: none;
}

.switch-link:hover {
  text-decoration: underline;
}

/* === Error Message === */
.error {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}
</style>
