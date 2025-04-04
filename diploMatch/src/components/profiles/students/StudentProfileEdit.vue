<template>
  <div class="profile-edit-container">
    <div class="profile-card">
      <h2 class="edit-title">Edit Profile</h2>
      <div class="profile-header">
        <div class="form-grid">
          <input type="text" v-model="profile.first_name" placeholder="Name" />
          <input
            type="text"
            v-model="profile.last_name"
            placeholder="Surname"
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

      <div class="section-title">Basic Info</div>
      <input type="text" v-model="profile.gpa" placeholder="GPA" />
      <input :value="authStore.user.email" readonly class="email-field" />
      <input
        type="url"
        v-model="profile.portfolio"
        placeholder="Portfolio (optional)"
      />

      <div class="section-title">Major</div>
      <select v-model="profile.specialization" class="select-input">
        <option value="" disabled hidden>Select your major</option>
        <option>Automation and Control</option>
        <option>Information Systems</option>
        <option>Computer Systems and Software</option>
        <option>IT Management</option>
        <option>Robotics and Mechatronics</option>
      </select>

      <div class="section-title">Skills</div>
      <div v-if="!authStore.user.is_profile_completed" class="skills-container">
        <div
          v-for="skill in skills"
          :key="skill.id"
          :class="[
            'skill-item',
            { selected: selectedSkills.includes(skill.id) },
          ]"
          @click="toggleSkill(skill.id)"
        >
          {{ skill.name }}
        </div>
      </div>
      <div v-else class="selected-skills">
        <div
          v-for="skill in selectedSkillsNames"
          :key="skill"
          class="skill-item selected"
        >
          {{ skill }}
        </div>
      </div>

      <!-- ✅ Button Section: Show Save or Save+Cancel depending on profile status -->
      <div class="button-row">
        <button class="save-btn" @click="saveProfile">Save</button>
        <button
          v-if="authStore.user.is_profile_completed"
          class="cancel-btn"
          @click="$router.push('/profile')"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../../../store/auth";
import axios from "axios";

const authStore = useAuthStore();
const router = useRouter();

const profile = ref({});
const skills = ref([]);
const team = ref(null);
const selectedSkills = ref([]);
const imageFile = ref(null);
const imagePreview = ref("");
const defaultAvatar = new URL(
  "../../../icons/default-avatar.png",
  import.meta.url
).href;
const editing = ref(true); // true by default since it's Edit Profile

const selectedSkillsNames = computed(() =>
  skills.value
    .filter((skill) => selectedSkills.value.includes(skill.id))
    .map((s) => s.name)
);

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

const toggleSkill = (id) => {
  if (authStore.user.is_profile_completed) return;
  if (selectedSkills.value.includes(id)) {
    selectedSkills.value = selectedSkills.value.filter((s) => s !== id);
  } else if (selectedSkills.value.length < 5) {
    selectedSkills.value.push(id);
  }
};

const fetchTeam = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    team.value = res.data;
  } catch (err) {
    console.error("Error loading team", err);
  }
};

onMounted(async () => {
  try {
    const skillsRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/skills/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );

    skills.value = skillsRes.data;

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
  } catch (err) {
    console.error("Error loading profile");
  }
});

const saveProfile = async () => {
  try {
    const formData = new FormData();
    Object.entries(profile.value).forEach(([key, val]) => {
      if (key !== "photo") {
        formData.append(key, val ?? "");
      }
    });
    if (imageFile.value) formData.append("photo", imageFile.value);
    selectedSkills.value.forEach((id) => formData.append("skill_ids", id));
    formData.append("user", authStore.user.id);

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

    authStore.user.is_profile_completed = true;
    await fetchTeam();
    router.push("/profile");
  } catch (err) {
    console.error("Error saving profile", err);
  }
};
</script>

<style scoped>
.profile-edit-container {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.profile-card {
  background: #eaf3fb; /* единый цвет */
  padding: 40px 32px;
  border-radius: 20px;
  width: 100%;
  max-width: 500px; /* одинаковый размер */
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

.edit-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  text-align: left;
}
.image-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  position: relative;
  width: 120px;
  height: 120px;
  margin-left: auto;
  margin-right: auto;
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

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.form-grid {
  display: flex;
  flex-direction: column;
  width: 65%;
  gap: 10px;
}

.profile-img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}

.upload-icon {
  margin-top: 6px;
  font-size: 16px;
  cursor: pointer;
  color: #555;
  display: flex;
  align-items: center;
  gap: 4px;
}

.upload-icon input {
  display: none;
}

input {
  width: 95%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
  background-color: white;
  transition: border-color 0.3s ease;
  margin-bottom: 12px; /* Отступ между инпутами */
}

input:focus {
  border-color: #007bff;
  outline: none;
}

.email-field {
  font-weight: 600;
  color: #333;
  background-color: #eaeaea;
  cursor: not-allowed;
}

.section-title {
  margin-top: 18px;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 8px;
}

.skills-container,
.selected-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
  margin-bottom: 25px;
  justify-content: center;
}

.skill-item {
  background-color: #f2f2f2;
  padding: 8px 20px; /* 🟢 Чуть вытянутее по ширине */
  border-radius: 20px; /* 🟢 Более округлые углы */
  font-size: 14px; /* 🟢 Средний размер текста */
  font-weight: 500;
  line-height: 1.4;
  cursor: pointer;
  border: 1px solid #ccc;
  transition: 0.2s ease;
}

.skill-item:hover {
  background-color: #0056b3;
}

.skill-item.selected {
  background: #80c5ff;
  color: black;
}
.select-input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
  margin-bottom: 12px;
  background-color: white;
  background-position: right 12px center;
  background-size: 16px;
  cursor: pointer;
}

.select-input:focus {
  border-color: #007bff;
  outline: none;
}

.button-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 25px;
}

.save-btn,
.cancel-btn {
  min-width: 120px;
  padding: 12px;
  font-size: 14px;
  border: none;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.save-btn {
  background-color: #007bff;
  color: white;
}

.save-btn:hover {
  background-color: #0056b3;
}

.cancel-btn {
  background-color: #d3d3d3;
  color: black;
}

.cancel-btn:hover {
  background-color: #bbb;
}
</style>
