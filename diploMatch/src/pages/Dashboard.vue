<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div
        v-if="!user?.is_profile_completed && showModal"
        class="modal-overlay"
      >
        <div class="modal-box">
          <h3>Complete your profile</h3>
          <p class="modal-text">
            To continue using the platform, please complete your profile.
          </p>
          <router-link to="/profile?edit=true" class="modal-btn">
            Complete Now
          </router-link>
        </div>
      </div>

      <h2 class="section-title">
        {{ isDean ? "Approved Projects" : "Projects for you" }}
        <button v-if="isDean" class="excel-btn" @click="downloadExcel">
          📥 Download .xlsx
        </button>
      </h2>

      <div
        v-for="project in paginatedProjects"
        :key="project.id"
        class="project-card"
      >
        <div class="project-header">
          <h3 class="project-title">{{ project.thesis_name }}</h3>
          <div class="project-actions" v-if="isDean">
            <button
              class="action-btn gray"
              title="Edit this project"
              @click="goToEditProject(project.thesis_id)"
            >
              <i class="fa-solid fa-pen"></i>
            </button>
          </div>

          <div class="actions" v-if="user?.role !== 'Dean Office'">
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
              :disabled="
                userHasTeam || userHasPendingRequest || isTeamFull(project)
              "
              @click="applyToTeam(project.id)"
              v-if="!isSupervisor"
            >
              {{
                isTeamFull(project)
                  ? "Team is full"
                  : userHasTeam
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
            :to="`/supervisors/${project.supervisor.id}`"
            :title="`${project.supervisor.first_name} ${project.supervisor.last_name} (Supervisor)`"
          >
            <img
              :src="getPhoto(project.supervisor)"
              class="avatar supervisor-avatar"
              alt="Supervisor"
            />
          </router-link>

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
            :class="getSkillClass(skill, project)"
          >
            {{ skill }}
          </span>
        </div>
      </div>

      <!-- ✅ Pagination Controls -->
      <div v-if="totalPages > 1" class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1">‹</button>
        <button
          v-for="page in totalPages"
          :key="page"
          @click="goToPage(page)"
          :class="{ active: currentPage === page }"
        >
          {{ page }}
        </button>
        <button @click="nextPage" :disabled="currentPage === totalPages">
          ›
        </button>
      </div>
    </div>

    <!-- ✅ Футер будет всегда снизу -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";
import { useLikeStore } from "../store/likes";
import { useRouter, useRoute } from "vue-router";
import Footer from "../components/Footer/Footer.vue";

const authStore = useAuthStore();
const likeStore = useLikeStore();
const isTeamFull = (project) => project?.members?.length >= 4;
const user = authStore.user;
const mySkills = ref([]);
const projects = ref([]);
const isDean = computed(() => user?.role === "Dean Office");
const isSupervisor = computed(() => user?.role === "Supervisor");
const showModal = ref(false);
const editingProjectId = ref(null);
const route = useRoute();
const router = useRouter();
const userHasTeam = computed(() => authStore.userHasTeam);
const userHasPendingRequest = computed(() => authStore.userHasPendingRequest);
// ✅ Pagination
const currentPage = ref(parseInt(route.query.page) || 1);
watch(
  () => route.query.page,
  (newPage) => {
    currentPage.value = parseInt(newPage) || 1;
  }
);
const projectsPerPage = 5;
const totalPages = computed(() =>
  Math.ceil(projects.value.length / projectsPerPage)
);
const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * projectsPerPage;
  return projects.value.slice(start, start + projectsPerPage);
});

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    router.push({ path: "/dashboard", query: { page: page } });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};
const goToEditProject = (projectId) => {
  router.push({ path: "/create-project", query: { edit: "true", projectId } });
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    goToPage(currentPage.value + 1);
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    goToPage(currentPage.value - 1);
  }
};
const toggleLike = async (projectId) => {
  await likeStore.toggleLike(projectId);
};
const getSkillClass = (skillName, project) => {
  const mySkillNames = mySkills.value.map((s) => s.toLowerCase());

  // Собираем все покрытые скиллы (именами) в команде
  const allCoveredSkills = new Set();
  project.members.forEach((member) => {
    member.skills?.forEach((s) => {
      allCoveredSkills.add(s.name.toLowerCase());
    });
  });

  const skill = skillName.toLowerCase();
  const isMySkill = mySkillNames.includes(skill);
  const isCovered = allCoveredSkills.has(skill);

  if (isMySkill && isCovered) return "skill-pill my-covered"; // 🟢🩶
  if (isMySkill && !isCovered) return "skill-pill my-unique"; // 🟢
  if (!isMySkill && isCovered) return "skill-pill covered"; // 🔵🩶
  return "skill-pill"; // 🔵
};

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
    await authStore.refreshTeamAndRequestStatus();
  } catch (err) {
    console.error("Failed to apply:", err);
    alert(err.response?.data?.error || "Failed to apply");
  }
};
const downloadExcel = async () => {
  try {
    const res = await axios.get(
      "http://127.0.0.1:8000/api/teams/export-excel/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
        responseType: "blob",
      }
    );

    const blob = new Blob([res.data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `diploma_projects_${new Date()
      .toLocaleDateString()
      .replaceAll("/", "_")}.xlsx`;
    link.click();
  } catch (err) {
    console.error("❌ Failed to download Excel:", err);
    alert("Something went wrong when downloading the file.");
  }
};
onMounted(async () => {
  try {
    if (!user?.is_profile_completed) showModal.value = true;
    await likeStore.fetchLikes();
    await authStore.refreshTeamAndRequestStatus();
    let endpoint = "http://127.0.0.1:8000/api/teams/";
    if (user?.role === "Dean Office") {
      endpoint = "http://127.0.0.1:8000/api/teams/approved/";
    }

    const res = await axios.get(endpoint, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    projects.value = res.data;

    projects.value = res.data;
    const profileRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/complete-profile/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    mySkills.value = profileRes.data.skills.map((s) => s.name.toLowerCase());
  } catch (err) {
    console.error("Error loading data:", err);
  }
});
</script>

<style scoped>
.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.dashboard-container {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 50px 20px;
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
  margin: 0px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.heart-icon {
  font-size: 20px;
  color: #ccc;
  cursor: pointer;
  padding-left: 10px;
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
  white-space: nowrap;
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
.excel-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 8px;
  margin-left: 20px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s ease;
}
.excel-btn:hover {
  background: #218838;
}
.project-members a {
  display: inline-block;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.project-members a:hover {
  transform: scale(1.05);
}
.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: 0.2s ease;
}

.action-btn i {
  color: white;
}

.gray {
  background-color: #a8a8a8;
}

.action-btn:hover {
  opacity: 0.9;
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
  font-family: Arial, sans-serif, "Segoe UI";
  color: black;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
}
.skill-pill.covered {
  background: #b1d0e9;
  color: #898787;
}

.skill-pill.my-unique {
  background: #83d481;
  color: black;
}

.skill-pill.my-covered {
  background: #9ede9c;
  color: #898787;
}
.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 20px;
}

.pagination button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background-color: #eee;
  cursor: pointer;
  font-weight: bold;
  color: #333;
}

.pagination button.active {
  background-color: #007bff;
  color: white;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>