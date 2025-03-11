<template>
  <div class="dashboard-container">
    <h2 class="welcome-title">Welcome, {{ user?.first_name }}!</h2>

    <!-- ✅ MODAL -->
    <div v-if="!user?.is_profile_completed && showModal" class="modal-overlay">
      <div class="modal-box">
        <h3>Complete your profile</h3>
        <p class="modal-text">
          To continue using the platform, please complete your profile.
        </p>
        <router-link to="/profile?edit=true" class="modal-btn">Complete Now</router-link>
      </div>
    </div>

    <!-- Your dashboard content -->
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../store/auth";

const authStore = useAuthStore();
const user = authStore.user;
const showModal = ref(false);

onMounted(() => {
  if (user && !user.is_profile_completed) {
    showModal.value = true;
  }
});
</script>

<style scoped>
.dashboard-container {
  padding: 40px;
  text-align: center;
}

.welcome-title {
  font-size: 28px;
  margin-bottom: 20px;
}

/* MODAL STYLING */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-box {
  background: #fff;
  padding: 30px 40px;
  border-radius: 12px;
  text-align: center;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-box h3 {
  font-size: 24px;
  margin-bottom: 10px;
}

.modal-text {
  font-size: 15px;
  margin-bottom: 20px;
}

.modal-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: 0.3s;
}

.modal-btn:hover {
  background-color: #0056b3;
}
</style>
