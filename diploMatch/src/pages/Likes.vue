<template>
  <div class="dashboard-container">
    <h2 class="section-title">Liked Projects</h2>

    <div v-if="projects.length === 0" class="empty-msg">
      No liked projects yet.
    </div>

    <div v-for="project in projects" :key="project.id" class="project-card">
      <div class="project-header">
        <h3 class="project-title">{{ project.thesis_name }}</h3>
        <div class="header-actions">
          <i
            class="fa-solid fa-heart heart-icon liked"
            @click="toggleLike(project.id)"
            title="Remove from favorites"
          ></i>
          <button
            class="apply-btn"
            v-if="!isSupervisor"
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

      <p class="project-description">{{ project.thesis_description }}</p>

      <div class="project-members">
        <router-link
          v-if="project.supervisor"
          :to="`/supervisors/${project.supervisor.user}`"
          :title="`${project.supervisor.first_name} ${project.supervisor.last_name} (Supervisor)`"
        >
          <img
            :src="getPhoto(project.supervisor)"
            class="avatar supervisor-avatar"
          />
        </router-link>

        <router-link
          v-for="member in getSortedMembers(project)"
          :key="member.user"
          :to="`/students/${member.user}`"
          :title="member.first_name + ' ' + member.last_name"
        >
          <img
            :src="getPhoto(member)"
            class="avatar"
            :class="{ 'owner-avatar': member.user === project.owner }"
          />
        </router-link>
      </div>

      <div class="project-skills">
        <span
          v-for="skill in project.required_skills"
          :key="skill.id || skill"
          :class="getSkillClass(skill, project)"
        >
          {{ skill.name || skill }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";
import { useLikeStore } from "../store/likes";

const authStore = useAuthStore();
const likeStore = useLikeStore();
const mySkills = ref([]);
const user = authStore.user;
const projects = ref([]);

const userHasTeam = computed(() => authStore.userHasTeam);
const userHasPendingRequest = computed(() => authStore.userHasPendingRequest);
const isSupervisor = computed(() => user?.role === "Supervisor");

const getPhoto = (person) => {
  const photoPath = person?.photo || person?.user?.photo;
  if (photoPath) {
    return photoPath.startsWith("http")
      ? photoPath
      : `http://127.0.0.1:8000${photoPath}`;
  }
  return new URL("../icons/default-avatar.png", import.meta.url).href;
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
    await authStore.refreshTeamAndRequestStatus();
  } catch (err) {
    console.error("Failed to apply:", err);
    alert(err.response?.data?.error || "Failed to apply");
  }
};

const getSortedMembers = (project) => {
  if (!project || !project.members) return [];
  const ownerId = project.owner;
  const members = [...project.members];
  members.sort((a, b) =>
    a.user === ownerId ? -1 : b.user === ownerId ? 1 : 0
  );
  return members;
};

const toggleLike = async (teamId) => {
  await likeStore.toggleLike(teamId);
  projects.value = projects.value.filter((p) => p.id !== teamId);
};
const getSkillClass = (skillName, project) => {
  const mySkillNames = mySkills.value
    .filter((s) => s && s.name)
    .map((s) => s.name.toLowerCase());

  const skill =
    skillName?.name?.toLowerCase?.() || skillName?.toLowerCase?.() || "";

  const isMySkill = mySkillNames.includes(skill);
  const isCovered = project.members?.some((member) =>
    member.skills?.some((s) => s.name?.toLowerCase() === skill)
  );

  if (isMySkill && isCovered) return "skill-pill my-covered";
  if (isMySkill) return "skill-pill my-unique";
  if (isCovered) return "skill-pill covered";
  return "skill-pill";
};
onMounted(async () => {
  try {
    if (!user) {
      await authStore.fetchUser();
    }

    const res = await axios.get("http://127.0.0.1:8000/api/teams/likes/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    projects.value = res.data;
    const profileRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/complete-profile/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    mySkills.value = profileRes.data.skills || [];
    await authStore.refreshTeamAndRequestStatus();
  } catch (err) {
    console.error("Failed to load liked projects:", err);
  }
});
</script>

<style scoped>
.dashboard-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 45px 20px;
  text-align: center;
}
.section-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
}
.empty-msg {
  font-size: 16px;
  color: #666;
  margin-top: 40px;
}
.project-card {
  background: #e6f0fb;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  text-align: left;
}
.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-title {
  font-size: 16px;
  font-weight: bold;
}
.heart-icon {
  font-size: 18px;
  color: #888;
  cursor: pointer;
  transition: color 0.3s;
}
.heart-icon.liked {
  color: red;
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
.apply-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.project-description {
  font-size: 14px;
  margin: 10px 0 16px 0;
}
.project-members {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}
.owner-avatar {
  border: 2px solid #28a745 !important;
}
.supervisor-avatar {
  border: 3px solid gold !important;
  box-shadow: 0 0 5px rgba(255, 215, 0, 0.8);
}
.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-pill {
  background: #80c5ff;
  color: black;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
}
.skill-pill.my-unique {
  background: #83d481;
  color: black;
}

.skill-pill.covered {
  background: #b1d0e9;
  color: #898787;
}

.skill-pill.my-covered {
  background: #9ede9c;
  color: #898787;
}

</style>
