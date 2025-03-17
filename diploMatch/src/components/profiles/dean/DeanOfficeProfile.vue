<template>
    <div class="profile-container">
      <div class="profile-card">
        <div class="header">
          <h2>My Profile</h2>
          <div class="actions">
            <button class="edit-btn" @click="editProfile">✏️ Edit Profile</button>
          </div>
        </div>
  
        <div class="profile-body">
          <div class="left">
            <img :src="profile.photo ? profile.photo : defaultAvatar" class="profile-image" />
          </div>
  
          <div class="right">
            <h3 class="name">{{ profile.first_name }} {{ profile.last_name }}</h3>
            <p class="email"><strong>Email:</strong> {{ profile.email }}</p>
            <p><strong>Job Role:</strong> {{ profile.job_role }}</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '../../../store/auth';
  import axios from 'axios';
  
  const router = useRouter();
  const authStore = useAuthStore();
  const profile = ref({});
  const defaultAvatar = new URL('../assets/default-avatar.png', import.meta.url).href;
  
  onMounted(async () => {
    const res = await axios.get("http://127.0.0.1:8000/api/profiles/complete-profile/", {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    profile.value = res.data;
  
    if (profile.value.photo && !profile.value.photo.startsWith("http")) {
      profile.value.photo = `http://127.0.0.1:8000${profile.value.photo}`;
    }
  });
  
  const editProfile = () => {
    router.push('/dean-profile/edit');
  };
  </script>
  
  <style scoped>
  .profile-container {
    padding-top: 100px;
    display: flex;
    justify-content: center;
  }
  .profile-card {
    width: 100%;
    max-width: 700px;
    padding: 30px;
    background: #f4f7fb;
    border-radius: 16px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
  }
  .actions {
    display: flex;
    gap: 10px;
  }
  .edit-btn {
    padding: 8px 16px;
    background: #007bff;
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: bold;
    cursor: pointer;
  }
  .profile-body {
    display: flex;
    gap: 20px;
    align-items: flex-start;
  }
  .left {
    flex-shrink: 0;
  }
  .profile-image {
    width: 120px;
    height: 120px;
    object-fit: cover;
    border-radius: 50%;
    border: 3px solid #007bff;
  }
  .right {
    flex-grow: 1;
  }
  .name {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
  }
  .email {
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
  }
  </style>