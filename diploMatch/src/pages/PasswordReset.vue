<template>
  <div class="password-reset-container">
    <div class="card">
      <img src="../assets/logo.png" alt="Diplomatch Logo" class="logo" />
      <p class="subtitle"><strong>Match. Collaborate. Graduate.</strong></p>

      <div v-if="!resetMode">
        <h2>Reset password via e-mail</h2>
        <form @submit.prevent="sendResetEmail">
          <input
            v-model="email"
            type="email"
            placeholder="E-mail"
            class="input-field"
            required
          />
          <button type="submit" class="btn">Send password reset email</button>
        </form>
        <p v-if="message" class="success-message">{{ message }}</p>
        <p v-if="error" class="error-message">{{ error }}</p>
      </div>

      <div v-else>
        <h2>Change your password</h2>
        <input
          v-model="password"
          type="password"
          placeholder="New Password"
          required
          class="input-field"
        />
        <input
          v-model="confirmPassword"
          type="password"
          placeholder="Confirm Password"
          required
          class="input-field"
        />
        <button @click="resetPassword" class="btn">Save changes</button>
        <p v-if="message" class="success-message">{{ message }}</p>
        <p v-if="error" class="error-message">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const API_URL = "http://127.0.0.1:8000/api/users";

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const message = ref("");
const error = ref("");
const resetMode = ref(false);
const uid = ref("");
const token = ref("");

// Check if URL contains uid & token → If so, switch to password reset mode
onMounted(() => {
  if (route.params.uid && route.params.token) {
    resetMode.value = true;
    uid.value = route.params.uid as string;
    token.value = route.params.token as string;
  }
});

// Send password reset email
const sendResetEmail = async () => {
  try {
    await axios.post(`${API_URL}/forgot-password/`, { email: email.value });
    message.value = "Password reset email sent! Check your inbox.";
    error.value = "";
  } catch (err) {
    error.value = "Failed to send password reset email.";
    message.value = "";
  }
};

// Reset password using token
const resetPassword = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match!";
    return;
  }

  try {
    await axios.put(`${API_URL}/reset-password/${uid.value}/${token.value}/`, {
      new_password: password.value,
      confirm_password: confirmPassword.value,
    });

    message.value = "Password successfully reset! Redirecting...";
    setTimeout(() => {
      router.push("/login");
    }, 2000);
  } catch (err) {
    error.value = "Failed to reset password.";
  }
};
</script>

<style scoped>
/* Center the form */
.password-reset-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 450px; /* Slightly wider */
}

.logo {
  width: 140px;
  margin-bottom: 8px;
}

.subtitle {
  color: #000000;
  font-size: 14px;
  margin-bottom: 15px;
}

/* Adjusted text styles */
h2 {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #144a77;
}

/* Input Styling */
.input-field {
  width: 100%;
  padding: 12px;
  margin: 12px 0;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  box-sizing: border-box;
}

/* Button Styling */
.btn {
  width: 100%;
  padding: 12px;
  background-color: #144a77;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  margin-top: 15px;
}

.btn:hover {
  background-color: #0d3659;
  transform: translateY(-2px);
}

/* Success & Error Messages */
.success-message {
  color: green;
  font-size: 14px;
  margin-top: 10px;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}
</style>
