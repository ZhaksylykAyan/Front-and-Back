<template>
  <div class="dashboard-container">
    <div v-if="!user?.is_profile_completed && showModal" class="modal-overlay">
      <div class="modal-box">
        <h3>Complete your profile</h3>
        <p class="modal-text">
          To continue using the platform, please complete your profile.
        </p>
        <router-link to="/profile?edit=true" class="modal-btn"
          >Complete Now</router-link
        >
      </div>
    </div>

    <h2 class="section-title">Projects for you</h2>

    <div v-for="project in projects" :key="project.id" class="project-card">
      <div class="project-header">
        <h3 class="project-title">{{ project.thesis_name }}</h3>
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

      <p class="project-description">{{ project.thesis_description }}</p>

      <div class="project-members">
        <!-- ✅ Supervisor first (if exists) -->
        <router-link
          v-if="project.supervisor"
          :to="`/supervisors/${project.supervisor.user}`"
          :title="`${project.supervisor.first_name} ${project.supervisor.last_name} (Supervisor)`"
        >
          <img
            :src="getPhoto(project.supervisor)"
            class="avatar supervisor-avatar"
            alt="Supervisor"
          />
        </router-link>

        <!-- ✅ Team members -->
        <router-link
          v-for="member in getSortedMembers(project)"
          :key="member.id"
          :to="`/students/${member.user}`"
          :title="member.first_name + ' ' + member.last_name"
        >
          <img
            :src="getPhoto(member)"
            class="avatar"
            :class="{ 'owner-avatar': member.user === project.owner }"
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
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";

const authStore = useAuthStore();
const projects = ref([]);
const user = authStore.user;
const showModal = ref(false);
const userHasTeam = ref(false);
const userHasPendingRequest = ref(false);

const getPhoto = (person) => {
  const photoPath = person?.photo || person?.user?.photo;
  if (photoPath) {
    return photoPath.startsWith("http")
      ? photoPath
      : `http://127.0.0.1:8000${photoPath}`;
  }
  return new URL("../icons/default-avatar.png", import.meta.url).href;
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
    console.error("Failed to apply:", err);
    alert(err.response?.data?.error || "Failed to apply");
  }
};

onMounted(async () => {
  try {
    if (authStore.user && !authStore.user.is_profile_completed) {
      showModal.value = true;
    }

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

    const res = await axios.get("http://127.0.0.1:8000/api/teams/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });

    projects.value = res.data;
  } catch (err) {
    console.error("Error loading data:", err);
  }
});
</script>

<style scoped>
.dashboard-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  text-align: center;
}
.section-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-box {
  background: #fff;
  padding: 30px 40px;
  border-radius: 12px;
  text-align: center;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-box h3 {
  font-size: 24px;
  margin-bottom: 10px;
}

.modal-text {
  font-size: 15px;
  margin-bottom: 20px;
}

.modal-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: 0.3s;
}

.modal-btn:hover {
  background-color: #0056b3;
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
.project-title {
  font-size: 16px;
  font-weight: bold;
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
  font-size: 14px;
  margin: 10px 0 16px 0;
}
.project-members {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.project-members a {
  display: inline-block;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.project-members a:hover {
  transform: scale(1.05);
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}
.owner-avatar {
  border: 3px solid gold !important;
  box-shadow: 0 0 5px rgba(255, 215, 0, 0.8);
}
.supervisor-avatar {
  border: 2px solid #28a745 !important;
}
.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-pill {
  background: #80C5FF;
  color: black;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
}
</style>
