<template>
  <div class="profile-edit-container">
    <div class="profile-edit-card">
      <h2 class="edit-title">Edit Profile</h2>

      <div class="top-row">
        <div class="input-group">
          <input
            v-model="profile.first_name"
            type="text"
            placeholder="First Name"
          />
          <input
            v-model="profile.last_name"
            type="text"
            placeholder="Last Name"
          />
        </div>

        <div class="image-wrapper">
          <img :src="imagePreview || defaultAvatar" class="profile-image" />
          <label class="upload-btn" v-if="editing">
            <input type="file" accept="image/*" @change="handleImageUpload" />
            <i class="fas fa-camera"></i>
          </label>
        </div>
      </div>

      <div class="form-section">
        <h3>Basic Info</h3>
        <input
          type="text"
          :value="authStore.user.email"
          disabled
          class="readonly-input"
        />
      </div>

      <div class="form-section">
        <h3>Degree</h3>
        <input
          v-model="profile.degree"
          type="text"
          placeholder="Enter Degree"
        />
      </div>

      <div class="form-section" v-if="!user.is_profile_completed">
        <h3>Skills (Choose up to {{ maxSkills }})</h3>
        <div class="skills-grid">
          <div
            v-for="skill in skills"
            :key="skill.id"
            :class="[
              'skill-card',
              { selected: selectedSkills.includes(skill.id) },
            ]"
            @click="toggleSkill(skill.id)"
          >
            {{ skill.name }}
          </div>
        </div>
      </div>

      <div class="form-section" v-else>
        <h3>Skills</h3>
        <div class="skills-grid readonly">
          <span
            v-for="skill in selectedSkillsNames"
            :key="skill.id"
            class="skill-card selected"
          >
            {{ skill }}
          </span>
        </div>
      </div>

      <div class="btn-group">
        <button class="save-btn" @click="updateProfile">Save Profile</button>
        <button
          class="cancel-btn"
          @click="cancelEdit"
          v-if="authStore.user.is_profile_completed"
        >
          Cancel
        </button>
      </div>

      <p v-if="successMessage" class="success-msg">{{ successMessage }}</p>
      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../../../store/auth";
import axios from "axios";

const router = useRouter();
const authStore = useAuthStore();
const user = authStore.user;

const profile = ref({});
const skills = ref([]);
const selectedSkills = ref([]);
const editing = ref(true);
const successMessage = ref("");
const errorMessage = ref("");
const imageFile = ref(null);
const imagePreview = ref("");
const defaultAvatar = new URL(
  "../../../icons/default-avatar.png",
  import.meta.url
).href;

const maxSkills = computed(() => 10);

const selectedSkillsNames = computed(() =>
  skills.value
    .filter((skill) => selectedSkills.value.includes(skill.id))
    .map((skill) => skill.name)
);

const toggleSkill = (id) => {
  if (user.is_profile_completed) return;
  if (selectedSkills.value.includes(id)) {
    selectedSkills.value = selectedSkills.value.filter((s) => s !== id);
  } else if (selectedSkills.value.length < maxSkills.value) {
    selectedSkills.value.push(id);
  }
};

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
    Object.entries(profile.value).forEach(([key, val]) => {
      if (key !== "photo") {
        formData.append(key, val ?? "");
      }
    });
    formData.append("user", user.id);
    selectedSkills.value.forEach((id) => formData.append("skill_ids", id));
    if (imageFile.value) {
      formData.append("photo", imageFile.value);
    }

    await axios.put(
      "http://127.0.0.1:8000/api/profiles/complete-profile/",
      formData,
      {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          "Content-Type": "multipart/form-data",
        },
      }
    );

    successMessage.value = "Profile updated successfully!";
    authStore.user.is_profile_completed = true;
    router.push("/profile");
  } catch (error) {
    errorMessage.value = "Error updating profile.";
  }
};

const cancelEdit = () => {
  router.push("/profile");
};

onMounted(async () => {
  try {
    const profileRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/complete-profile/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    profile.value = profileRes.data;
    selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];

    if (profile.value.photo) {
      imagePreview.value = profile.value.photo.startsWith("http")
        ? profile.value.photo
        : `http://127.0.0.1:8000${profile.value.photo}`;
    }

    const skillsRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/skills/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    skills.value = skillsRes.data;
  } catch (err) {
    errorMessage.value = "Failed to load profile.";
  }
});
</script>

<style scoped>
.profile-edit-container {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.profile-edit-card {
  background: #eaf3fb;
  padding: 40px 32px;
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

.edit-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.top-row {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
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

input:focus {
  border-color: #007bff;
  outline: none;
}

.readonly-input {
  background: #f2f2f2;
  color: #333;
  font-weight: 500;
  cursor: not-allowed;
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
  object-fit: cover;
  border: 3px solid #007bff;
}

.upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #007bff;
  border-radius: 50%;
  padding: 8px;
  cursor: pointer;
  color: white;
  font-size: 16px;
}

.upload-btn input {
  display: none;
}

.form-section {
  margin-top: 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  margin-top: 20px;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.skill-card {
  background: #f0f0f0;
  padding: 10px 18px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13.5px;
  font-weight: 500;
  transition: 0.3s;
}

.skill-card:hover {
  background-color: #dceaff;
}

.skill-card.selected {
  background: #80c5ff;
  color: black;
}

.btn-group {
  margin-top: 30px;
  display: flex;
  gap: 14px;
}

.save-btn {
  flex: 1;
  background: #007bff;
  color: white;
  padding: 12px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
}

.save-btn:hover {
  background: #0056b3;
}

.cancel-btn {
  flex: 1;
  background: #d3d3d3;
  color: #333;
  padding: 12px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
}

.cancel-btn:hover {
  background: #bbb;
}

.success-msg,
.error-msg {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  font-weight: 500;
}

.success-msg {
  color: green;
}

.error-msg {
  color: red;
}
</style>
