<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <h2 class="section-title">My Profile</h2>
        <div class="profile-actions" v-if="!isViewingOther && !editing">
          <button class="edit-btn" @click="goToEdit">✏️ Edit Profile</button>
          <button class="create-btn" @click="goToCreateProject">➕ Create Project</button>
        </div>
      </div>

      <div class="profile-body">
        <div class="left-column">
          <img :src="imageUrl" alt="profile image" class="profile-image" />
        </div>

        <div class="right-column">
          <h3 class="user-name">
            {{ profile.first_name }} {{ profile.last_name }}
          </h3>
          <a v-if="profile.user"> {{ profile.user_email }} </a>
          <div class="info-section">
            <p>{{ profile.degree }}</p>
          </div>

          <div class="info-section">
            <h4>Skills</h4>
            <div class="skills-grid">
              <span
                v-for="skill in selectedSkillsNames"
                :key="skill"
                class="skill-chip"
              >
                {{ skill }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- My Projects -->
    <div v-if="!isViewingOther && myProjects.length > 0" class="projects-section">
      <div class="projects-header">
        <h2 class="section-title">My Projects</h2>
        <div class="project-count">
          {{ myProjects.length }} out of 10 left
        </div>
      </div>

      <div
        v-for="project in myProjects"
        :key="project.id"
        class="project-card"
      >
        <div class="project-header">
          <h3 class="project-title">{{ project.thesis_name }}</h3>
          <div class="project-actions">
            <button class="edit-icon">✏️</button>
            <button class="view-icon">👁️</button>
            <button class="delete-icon">🗑️</button>
          </div>
        </div>

        <p class="project-description">
          {{ project.thesis_description }}
        </p>

        <div class="team-members">
          <img
            v-for="member in project.members"
            :key="member.user"
            :src="getPhoto(member)"
            :alt="member.first_name"
            class="avatar"
          />
        </div>

        <div class="project-skills">
          <span
            v-for="skill in project.required_skills"
            :key="skill"
            class="skill-pill"
          >
            {{ skill }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "../../../store/auth";

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const profile = ref({});
const skills = ref([]);
const selectedSkills = ref([]);
const myProjects = ref([]);
const isViewingOther = computed(() => !!route.params.id);

const imageUrl = computed(() =>
  profile.value.photo
    ? profile.value.photo.startsWith("http")
      ? profile.value.photo
      : `http://127.0.0.1:8000${profile.value.photo}`
    : new URL("../../../icons/default-avatar.png", import.meta.url).href
);

const selectedSkillsNames = computed(() =>
  skills.value
    .filter((skill) => selectedSkills.value.includes(skill.id))
    .map((skill) => skill.name)
);

const getPhoto = (member) => {
  if (member.photo) {
    return member.photo.startsWith("http")
      ? member.photo
      : `http://127.0.0.1:8000${member.photo}`;
  }
  return new URL("../../../icons/default-avatar.png", import.meta.url).href;
};

const goToCreateProject = () => {
  router.push("/create-project");
};

const goToEdit = () => {
  router.push({ path: "/profile", query: { edit: "true" } });
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

    if (isViewingOther.value) {
      const profileRes = await axios.get(
        `http://127.0.0.1:8000/api/profiles/supervisors/${route.params.id}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profile.value.skills?.map((s) => s.id) || [];
    } else {
      const profileRes = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profile.value.skills?.map((s) => s.id) || [];

      // ✅ Получить проекты
      const projectsRes = await axios.get(
        "http://127.0.0.1:8000/api/teams/my/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );

      // 📦 Поддержка обоих вариантов ответа: один объект (студент) или массив (супервизор)
      if (Array.isArray(projectsRes.data)) {
        myProjects.value = projectsRes.data;
      } else {
        myProjects.value = [projectsRes.data];
      }
    }
  } catch (error) {
    console.error("Error loading profile or projects:", error);
  }
});
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
  max-width: 900px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.profile-actions {
  display: flex;
  gap: 10px;
}

.edit-btn,
.create-btn {
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
}

.edit-btn {
  background-color: #28a745;
  color: white;
}

.create-btn {
  background-color: #007bff;
  color: white;
}

.profile-body {
  display: flex;
  gap: 30px;
  margin-top: 30px;
}

.left-column {
  flex: 1;
}

.profile-image {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #007bff;
}

.right-column {
  flex: 2;
}

.user-name {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 5px;
}

.info-section {
  margin-bottom: 15px;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.skill-chip {
  background: #80C5FF;
  color: black;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.projects-section {
  max-width: 1100px;
  padding-left: 30px;
}

.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.project-count {
  background: #ccc;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 14px;
}

.project-card {
  background: #e6f0ff;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 20px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 6px;
}

.project-description {
  font-size: 15px;
  color: #444;
  margin-bottom: 10px;
}

.project-actions {
  display: flex;
  gap: 8px;
}

.edit-icon,
.view-icon,
.delete-icon {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.skill-pill {
  background-color: #80C5FF;
  color: black;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}

.team-members {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  margin-bottom: 10px;
}

.team-members .avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}
</style>
