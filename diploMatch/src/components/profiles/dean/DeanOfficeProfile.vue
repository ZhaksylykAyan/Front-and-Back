<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="header">
        <h2>My Profile</h2>
      </div>
      <div class="profile-body">
        <div class="left">
          <div class="avatar-wrapper" @click="triggerUpload">
            <img :src="profile.photo || defaultAvatar" class="profile-image" />
            <div class="overlay">
              <i class="fas fa-camera"></i>
            </div>
            <input type="file" ref="fileInput" class="hidden" @change="uploadAvatar" />
          </div>
        </div>

        <div class="right">
          <h3 class="name">{{ profile.first_name }} {{ profile.last_name }}</h3>
          <p class="role"> {{ capitalize(profile.job_role) }}</p>
          <a href="#" class="email">{{ authStore.user.email }}</a>
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

const fileInput = ref(null);
const router = useRouter();
const authStore = useAuthStore();
const profile = ref({});
const defaultAvatar = new URL('../assets/default-avatar.png', import.meta.url).href;

const triggerUpload = () => {
  fileInput.value.click();
};

const uploadAvatar = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("photo", file);
  formData.append("user", authStore.user.id);

  try {
    await axios.put("http://127.0.0.1:8000/api/profiles/complete-profile/", formData, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        "Content-Type": "multipart/form-data",
      },
    });

    // обновим аватар
    profile.value.photo = URL.createObjectURL(file);
  } catch (err) {
    console.error("Failed to upload avatar", err);
  }
};

onMounted(async () => {
  const res = await axios.get("http://127.0.0.1:8000/api/profiles/complete-profile/", {
    headers: { Authorization: `Bearer ${authStore.token}` }
  });
  profile.value = res.data;

  if (profile.value.photo && !profile.value.photo.startsWith("http")) {
    profile.value.photo = `http://127.0.0.1:8000${profile.value.photo}`;
  }
});
const capitalize = (text) => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1);
};
const editProfile = () => {
  router.push({ path: "/profile", query: { edit: "true" } });
};
</script>

<style scoped>
.profile-container {
  padding-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.profile-card {
  width: 100%;
  max-width: 900px;
  padding: 30px;
  border-radius: 16px;
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
.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
}

.overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-size: 22px;
}

.avatar-wrapper:hover .overlay {
  opacity: 1;
}

.hidden {
  display: none;
}

.right {
  flex-grow: 1;
}

.name {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 10px;
}

.role {
  color: #898787
}

.email {
  margin-bottom: 10px;
  color: #1C97FE
}
</style>