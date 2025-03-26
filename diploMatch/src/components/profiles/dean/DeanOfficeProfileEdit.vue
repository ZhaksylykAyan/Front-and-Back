<template>
  <div class="profile-edit-container">
    <div class="profile-edit-card">
      <h2 class="edit-title">Edit Profile</h2>

      <div class="top-row">
        <div class="input-group">
          <input v-model="profile.first_name" placeholder="First Name" :disabled="authStore.user.is_profile_completed"/>
          <input v-model="profile.last_name" placeholder="Last Name" :disabled="authStore.user.is_profile_completed"/>
        </div>

        <div class="image-wrapper">
          <img :src="imagePreview || defaultAvatar" class="profile-image" />
          <label class="upload-btn">
            <input type="file" @change="handleImageUpload" />
            <i class="fas fa-camera"></i>
          </label>
        </div>
      </div>

      <div class="form-section">
        <h3>Basic Info</h3>
        <input type="text" :value="authStore.user.email" class="readonly-input" disabled />
      </div>

      <div class="form-section">
        <select v-model="profile.job_role" :disabled="authStore.user.is_profile_completed">
          <option value="dean">Dean</option>
          <option value="manager">Manager</option>
        </select>
      </div>

      <div class="btn-group">
        <button class="save-btn" @click="updateProfile">Save Profile</button>
        <button class="cancel-btn" @click="cancelEdit" v-if="authStore.user.is_profile_completed">Cancel</button>
      </div>

      <p v-if="successMessage" class="success-msg">{{ successMessage }}</p>
      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../../store/auth';
import axios from 'axios';

const authStore = useAuthStore();
const router = useRouter();

const profile = ref({});
const defaultAvatar = new URL(
"../../../icons/default-avatar.png",
import.meta.url
).href;
const imageFile = ref(null);
const imagePreview = ref('');
const successMessage = ref('');
const errorMessage = ref('');

onMounted(async () => {
  const res = await axios.get("http://127.0.0.1:8000/api/profiles/complete-profile/", {
    headers: { Authorization: `Bearer ${authStore.token}` }
  });
  profile.value = res.data;
  if (profile.value.photo && !profile.value.photo.startsWith("http")) {
    imagePreview.value = `http://127.0.0.1:8000${profile.value.photo}`;
  } else {
    imagePreview.value = profile.value.photo;
  }
});

const handleImageUpload = (e) => {
  const file = e.target.files[0];
  if (file) {
    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (event) => {
      imagePreview.value = event.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const updateProfile = async () => {
  try {
    const formData = new FormData();
    Object.entries(profile.value).forEach(([key, value]) =>
      formData.append(key, value ?? '')
    );
    formData.append('user', authStore.user.id);
    if (imageFile.value) formData.append('photo', imageFile.value);

    await axios.put("http://127.0.0.1:8000/api/profiles/complete-profile/", formData, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'multipart/form-data'
      }
    });

    successMessage.value = "Profile updated successfully!";
    setTimeout(() => router.push("/profile"), 1000);
  } catch (err) {
    errorMessage.value = "Failed to update profile.";
  }
};

const cancelEdit = () => {
  router.push("/profile");
};
</script>

<style scoped>
.profile-edit-container {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}
.profile-edit-card {
  background: #eef4f8;
  padding: 40px 32px;
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}
.edit-title {
  font-size: 22px;
    font-weight: bold;
    margin-bottom: 20px;
  }
  .top-row {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: center;
  }
  .input-group {
    flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 65%;
  }
  input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #ccc;
  font-size: 15px;
  background-color: white;
  transition: border-color 0.3s ease;
}
input:disabled,
select:disabled {
  background-color: #f0f0f0;
  color: #888;
  cursor: not-allowed;
  border: 1px solid #ccc;
}
  .image-wrapper {
    position: relative;
    width: 120px;
    height: 120px;
  }
  .profile-image {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 3px solid #007bff;
    object-fit: cover;
  }
  .upload-btn {
    position: absolute;
    bottom: 0;
    right: 0;
    background: #007bff;
    padding: 6px;
    border-radius: 50%;
    color: white;
    cursor: pointer;
  }
  .upload-btn input {
    display: none;
  }
  .form-section {
    margin-top: 20px;
  }
  .readonly-input {
    background: #f2f2f2;
    color: #333;
    font-weight: bold;
    max-width: 93%;
    cursor: not-allowed;
  }
  select {
    width: 100%;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #ccc;
  }
  .btn-group {
    margin-top: 25px;
    display: flex;
    gap: 12px;
  }
  .save-btn {
    flex: 1;
    background: #007bff;
    color: white;
    padding: 10px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
  }
  .cancel-btn {
    flex: 1;
    background: #ccc;
    color: #333;
    padding: 10px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
  }
  .success-msg {
    color: green;
    text-align: center;
    margin-top: 10px;
  }
  .error-msg {
    color: red;
    text-align: center;
    margin-top: 10px;
  }
  </style>