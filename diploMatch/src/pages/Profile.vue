<template>
  <div class="profile-container">
    <div class="profile-card">
      <!-- Profile Image -->
      <div class="image-section">
        <img :src="imagePreview || defaultAvatar" class="profile-image" />
        <label v-if="editing" class="upload-icon">
          <input type="file" @change="handleImageUpload" accept="image/*" />
          <i class="fas fa-camera"></i>
        </label>
      </div>

      <!-- Name and Action Buttons -->
      <div class="profile-info">
        <h2>{{ profile.first_name }} {{ profile.last_name }}</h2>
        <div class="action-buttons">
          <button class="edit-btn" @click="toggleEdit">✏️ Edit Profile</button>
          <button class="create-btn">➕ Create Project</button>
        </div>
      </div>

      <!-- Profile Form -->
      <form v-if="editing" @submit.prevent="updateProfile" class="profile-form">
        <div class="form-section">
          <label>First Name:</label>
          <input v-model="profile.first_name" type="text" required />

          <label>Last Name:</label>
          <input v-model="profile.last_name" type="text" required />
        </div>

        <div v-if="user.role === 'Student'" class="form-section">
          <label>Specialization:</label>
          <input v-model="profile.specialization" type="text" required />

          <label>GPA:</label>
          <input v-model="profile.gpa" type="number" step="0.01" required />

          <label>Portfolio (optional):</label>
          <input v-model="profile.portfolio" type="url" />
        </div>

        <div v-if="user.role === 'Supervisor'" class="form-section">
          <label>Degree:</label>
          <input v-model="profile.degree" type="text" required />
        </div>

        <div v-if="user.role === 'Dean Office'" class="form-section">
          <label>Job Role:</label>
          <select v-model="profile.job_role" required>
            <option value="manager">Manager</option>
            <option value="dean">Dean</option>
          </select>
        </div>

        <!-- SKILLS Section -->
        <div v-if="!user.is_profile_completed" class="form-section">
          <label>Skills (Choose up to {{ maxSkills }}):</label>
          <div class="skills-grid">
            <div
              v-for="skill in skills"
              :key="skill.id"
              :class="['skill-card', { selected: selectedSkills.includes(skill.id) }]"
              @click="toggleSkill(skill.id, maxSkills)"
            >
              {{ skill.name }}
            </div>
          </div>
        </div>

        <div v-else class="form-section">
          <label>Skills:</label>
          <div class="skills-grid readonly">
            <span
              v-for="skill in selectedSkillsNames"
              :key="skill"
              class="skill-card selected"
            >
              {{ skill }}
            </span>
          </div>
        </div>

        <!-- Buttons -->
        <button type="submit" class="save-btn">Save Profile</button>
        <button type="button" class="cancel-btn" @click="toggleEdit">Cancel</button>
      </form>

      <p v-if="successMessage" class="success-msg">{{ successMessage }}</p>
      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import axios from "axios";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const user = authStore.user;
const profile = ref({});
const skills = ref([]);
const selectedSkills = ref([]);
const imageFile = ref(null);
const imagePreview = ref("");
const editing = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const defaultAvatar = "../icons/default-avatar.jpg";

// Determine max skills by role
const maxSkills = computed(() => (user.role === "Student" ? 5 : 10));

// Get only selected skill names
const selectedSkillsNames = computed(() =>
  skills.value.filter(skill => selectedSkills.value.includes(skill.id)).map(skill => skill.name)
);

// Toggle edit mode
const toggleEdit = () => {
  editing.value = !editing.value;
};

// Handle image upload
const handleImageUpload = (e) => {
  const file = e.target.files[0];
  if (file) {
    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// Toggle skill selection
const toggleSkill = (id, max) => {
  if (user.is_profile_completed) return;
  if (selectedSkills.value.includes(id)) {
    selectedSkills.value = selectedSkills.value.filter((s) => s !== id);
  } else if (selectedSkills.value.length < max) {
    selectedSkills.value.push(id);
  }
};

// Load initial data
onMounted(async () => {
  try {
    if (!user) return router.push("/login");

    // Load skills
    const skillsRes = await axios.get("http://127.0.0.1:8000/api/profiles/skills/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    skills.value = skillsRes.data;

    // Load profile
    const profileRes = await axios.get("http://127.0.0.1:8000/api/profiles/complete-profile/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    profile.value = profileRes.data;
    selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];

    // Show image preview if exists
    if (profile.value.photo) {
      imagePreview.value = profile.value.photo.startsWith("http")
        ? profile.value.photo
        : `http://127.0.0.1:8000${profile.value.photo}`;
    }

    // Enable edit mode if route has ?edit=true
    if (route.query.edit === "true") {
      editing.value = true;
    }

  } catch (err) {
    errorMessage.value = "Failed to load profile.";
  }
});

// Save Profile
const updateProfile = async () => {
  try {
    const formData = new FormData();
    Object.keys(profile.value).forEach((key) => {
      formData.append(key, profile.value[key] ?? "");
    });

    formData.append("user", user.id);
    if (!user.is_profile_completed) {
      selectedSkills.value.forEach((id) => formData.append("skill_ids", id));
    }
    if (imageFile.value) formData.append("photo", imageFile.value);

    await axios.put("http://127.0.0.1:8000/api/profiles/complete-profile/", formData, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        "Content-Type": "multipart/form-data",
      },
    });

    successMessage.value = "Profile updated successfully!";
    authStore.user.is_profile_completed = true;
    editing.value = false;

    setTimeout(() => router.push("/"), 1500);

  } catch (err) {
    errorMessage.value = "Error updating profile. Please check fields.";
  }
};
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  padding-top: 100px;
  padding-left: 15px;
  padding-right: 15px;
}

.profile-card {
  width: 100%;
  max-width: 650px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
}

.image-section {
  display: flex;
  justify-content: center;
  position: relative;
}

.profile-image {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  border: 3px solid #007bff;
  object-fit: cover;
}

.upload-icon {
  position: absolute;
  bottom: 0;
  right: 40%;
  background: #007bff;
  padding: 6px;
  color: white;
  border-radius: 50%;
  cursor: pointer;
}

.upload-icon input {
  display: none;
}

.profile-info {
  text-align: center;
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.edit-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}

.create-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}

.form-section {
  margin-top: 20px;
}

input, select {
  width: 100%;
  padding: 10px;
  margin-top: 5px;
  margin-bottom: 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-card {
  padding: 8px 14px;
  border-radius: 16px;
  background: #eee;
  font-size: 13px;
  cursor: pointer;
  border: 2px solid #ccc;
  transition: 0.3s;
}

.skill-card.selected {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.save-btn {
  width: 100%;
  background: #007bff;
  color: white;
  padding: 12px;
  margin-top: 10px;
  border-radius: 8px;
  font-size: 16px;
  border: none;
}

.cancel-btn {
  width: 100%;
  background: #ccc;
  color: black;
  padding: 12px;
  margin-top: 8px;
  border-radius: 8px;
  font-size: 16px;
  border: none;
}

.success-msg {
  color: green;
  margin-top: 12px;
  text-align: center;
}

.error-msg {
  color: red;
  margin-top: 12px;
  text-align: center;
}
</style>
