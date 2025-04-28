<template>
    <div class="register-container">
      <div class="register-box">
        <img src="../assets/logo.png" alt="Diplomatch Logo" class="logo" />
        <p class="tagline"><strong>Match. Collaborate. Graduate.</strong></p>
  
        <h2>Create an account</h2>
  
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <input v-model="email" type="email" id="email" required placeholder="Enter your email" />
          </div>
  
          <div class="form-group">
            <input v-model="password" type="password" id="password" required placeholder="Enter your password" />
          </div>
  
          <div class="form-group">
            <input v-model="confirmPassword" type="password" id="confirmPassword" required placeholder="Confirm your password" />
            <p v-if="passwordMismatch" class="error-message">Passwords do not match!</p>
          </div>
  
          <button type="submit" :disabled="isLoading">
            {{ isLoading ? "Registering..." : "Register" }}
          </button>
  
          <p class="redirect">
            Already have an account? <router-link to="/login">Login</router-link>
          </p>
        </form>
  
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from "vue";
  import { useAuthStore } from "../store/auth";
  import { useRouter } from "vue-router";
  
  const email = ref("");
  const password = ref("");
  const confirmPassword = ref("");
  const errorMessage = ref("");
  const isLoading = ref(false);
  const authStore = useAuthStore();
  const router = useRouter();
  
  const passwordMismatch = ref(false);
  
  const handleRegister = async () => {
    errorMessage.value = "";
    passwordMismatch.value = password.value !== confirmPassword.value;
  
    if (passwordMismatch.value) {
      return;
    }
  
    isLoading.value = true;
  
    try {
      await authStore.register(email.value, password.value, confirmPassword.value);
      router.push("/login"); // Redirect to login page after success
    } catch (error) {
      errorMessage.value = error.message;
    } finally {
      isLoading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f4f4f4;
  }
  
  .register-box {
    background: white;
    padding: 3rem;
    border-radius: 12px;
    box-shadow: 0px 6px 14px rgba(0, 0, 0, 0.12);
    text-align: center;
    width: 496px;
  }
  
  .logo {
    width: 140px;
    margin-bottom: 0.8rem;
  }
  
  .tagline {
    font-size: 1rem;
    color: #000000;
    margin-bottom: 1.5rem;
  }
  
  h2 {
    margin-bottom: 1.2rem;
    color: #144A77;
    font-size: 1.6rem;
  }
  
  .form-group {
    margin-bottom: 1.2rem;
    text-align: left;
  }
  
  label {
    display: block;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }
  
  input {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
  }
  
  button {
    width: 100%;
    padding: 0.9rem;
    background: #1e40af;;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 1.1rem;
    cursor: pointer;
    transition: background 0.3s;
  }
  
  button:hover {
    background: #0f3a5e;
  }
  
  button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
  
  .redirect {
    margin-top: 1.2rem;
  }
  
  .error-message {
    color: red;
    font-size: 1rem;
  }
  </style>
  