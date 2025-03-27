<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <h2 class="section-title">My Profile</h2>
        <div class="profile-actions" v-if="!isViewingOther && !editing">
          <button class="edit-btn" @click="goToEdit">✏️ Edit Profile</button>
          <button class="create-btn" @click="goToCreateProject">
            ➕ Create Project
          </button>
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

    <!-- Projects Section -->
    <div v-if="myProjects.length > 0" class="projects-section">
      <div class="projects-header">
        <h2 class="section-title">
          {{ isViewingOther ? "Supervised Projects" : "My Projects" }}
        </h2>
        <div class="project-count">{{ myProjects.length }} out of 10 left</div>
      </div>

      <div v-for="project in myProjects" :key="project.id" class="project-card">
        <div class="project-header">
          <h3 class="project-title">{{ project.thesis_name }}</h3>
          <!-- Actions for owner -->
          <div class="project-actions" v-if="!isViewingOther">
            <span><i class="fa-regular fa-pen"></i></span>
            <button class="view-icon">👁️</button>
            <button class="delete-icon">🗑️</button>
          </div>
          <!-- ❤️ Like + Apply for others -->
          <div class="actions" v-else>
            <i
              :class="[
                'heart-icon',
                likeStore.likedProjectIds.includes(project.id)
                  ? 'fa-solid fa-heart'
                  : 'fa-regular fa-heart',
              ]"
              @click="toggleLike(project.id)"
              title="Add to favorites"
            ></i>
            <button
              class="apply-btn"
              :disabled="userHasTeam || userHasPendingRequest"
              @click="applyToTeam(project.id)"
            >
              {{
                userHasTeam
                  ? "Already in a team"
                  : userHasPendingRequest
                  ? "Applied"
                  : "Apply"
              }}
            </button>
          </div>
        </div>

        <p class="project-description">
          {{ project.thesis_description }}
        </p>

        <div class="team-members">
          <!-- 🟢 Сначала — Супервайзер -->
          <router-link
            v-if="project.supervisor"
            :to="`/supervisors/${project.supervisor.id}`"
            :title="`${project.supervisor.first_name} ${project.supervisor.last_name} (Supervisor)`"
          >
            <img
              :src="getPhoto(project.supervisor)"
              class="avatar supervisor-avatar"
              alt="Supervisor"
            />
          </router-link>

          <!-- 🧑‍💻 Затем — Участники -->
          <router-link
            v-for="member in project.members"
            :key="member.user"
            :to="`/students/${member.user}`"
            :title="`${member.first_name} ${member.last_name}`"
          >
            <img
              :src="getPhoto(member)"
              class="avatar"
              :alt="member.first_name"
            />
          </router-link>
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
import { useLikeStore } from "../../../store/likes";
const likeStore = useLikeStore();
const userHasTeam = ref(false);
const userHasPendingRequest = ref(false);
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const profile = ref({});
const skills = ref([]);
const selectedSkills = ref([]);
const myProjects = ref([]);
const isViewingOther = computed(() => !!route.params.id);

const toggleLike = async (projectId) => {
  await likeStore.toggleLike(projectId);
};
const applyToTeam = async (teamId) => {
  if (userHasTeam.value || userHasPendingRequest.value) return;
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/${teamId}/join/`,
      {},
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    alert("Join request sent!");
    userHasPendingRequest.value = true;
  } catch (err) {
    console.error("Apply failed:", err);
    alert(err.response?.data?.error || "Failed to apply");
  }
};
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
  await likeStore.fetchLikes();

  try {
    // ✅ Загрузка всех скиллов
    const skillsRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/skills/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    skills.value = skillsRes.data;

    if (isViewingOther.value) {
      // ✅ Загрузка чужого профиля супервизора
      const profileRes = await axios.get(
        `http://127.0.0.1:8000/api/profiles/supervisors/${route.params.id}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profile.value.skills?.map((s) => s.id) || [];
      myProjects.value = profile.value.projects || [];
    } else {
      // ✅ Загрузка своего профиля супервизора
      const profileRes = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profile.value.skills?.map((s) => s.id) || [];

      const projectsRes = await axios.get(
        "http://127.0.0.1:8000/api/teams/my/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      myProjects.value = Array.isArray(projectsRes.data)
        ? projectsRes.data
        : [projectsRes.data];
    }

    // ✅ Проверка на наличие команды
    const userProfileRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/complete-profile/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    userHasTeam.value = userProfileRes.data?.team !== null;

    // ✅ Проверка на наличие запроса
    try {
      const reqRes = await axios.get(
        "http://127.0.0.1:8000/api/teams/my-join-request/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      userHasPendingRequest.value = reqRes.data.status === "pending";
    } catch {
      userHasPendingRequest.value = false;
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
  background: #80c5ff;
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
  background: #ADADAD;
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

.heart-icon {
  font-size: 20px;
  color: #ccc;
  margin-right: 10px;
  cursor: pointer;
  transition: color 0.3s ease;
}
.heart-icon:hover {
  color: #ff6666;
}
.fa-solid.fa-heart {
  color: #ef6f6f;
}
.apply-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: 0.2s ease;
}
.apply-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  color: #666;
}
.apply-btn:hover {
  background-color: #0056b3;
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
  background-color: #80c5ff;
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
.supervisor-avatar {
  border: 2px solid #28a745 !important; /* зеленая рамка */
}
</style>