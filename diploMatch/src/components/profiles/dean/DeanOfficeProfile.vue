<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2 class="section-title">My Profile</h2>

      <div class="profile-body">
        <div class="avatar-wrapper" @click="triggerUpload">
          <img :src="profile.photo || defaultAvatar" class="profile-image" />
          <div class="overlay">
            <i class="fas fa-camera"></i>
          </div>
          <input type="file" ref="fileInput" class="hidden" @change="uploadAvatar" />
        </div>

        <div class="profile-info">
          <h3 class="name">{{ profile.first_name }} {{ profile.last_name }}</h3>
          <p class="role">{{ capitalize(profile.job_role) }}</p>
          <a href="#" class="email">{{ authStore.user.email }}</a>
        </div>
      </div>

      <div class="download-section">
        <h3>Download approved projects?</h3>
        <button class="download-btn">Download xlsx</button>
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
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding: 30px;
}

.profile-card {
  padding: 30px;
  border-radius: 16px;
  width: 100%;
  max-width: 1000px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 30px;
}

.profile-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
  margin-bottom: 40px;
}

.avatar-wrapper {
  position: relative;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #1c97fe;
  cursor: pointer;
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  color: white;
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: 0.3s ease;
}

.avatar-wrapper:hover .overlay {
  opacity: 1;
}

.hidden {
  display: none;
}

.profile-info {
  flex-grow: 1;
}

.name {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.role {
  font-size: 16px;
  color: #888;
  margin-bottom: 10px;
}

.email {
  color: #1c97fe;
  font-weight: 500;
  text-decoration: underline;
}

.download-section h3 {
  font-size: 18px;
  margin-bottom: 10px;
}

.download-btn {
  padding: 8px 16px;
  border: 1px solid #1c97fe;
  background: white;
  color: #1c97fe;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.2s ease;
}

.download-btn:hover {
  background: #1c97fe;
  color: white;
}
</style>