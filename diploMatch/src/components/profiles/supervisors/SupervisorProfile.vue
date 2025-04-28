<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <h2 class="section-title" v-if="!isViewingOther">{{ "My Profile" }}</h2>
        <div class="profile-actions" v-if="!isViewingOther && !editing">
          <button class="edit-btn" @click="goToEdit">
            <i class="fa-solid fa-pen" style="margin-right: 6px"></i>
            Edit Profile
          </button>
          <button class="create-btn" @click="goToCreateProject">
            <i class="fa-solid fa-plus" style="margin-right: 6px"></i>
            Create Project
          </button>
        </div>
      </div>

      <div class="profile-body">
        <div class="left-column">
          <img :src="imageUrl" alt="profile image" class="profile-image" />
        </div>

        <div class="right-column">
          <div class="info-header">
            <h3 class="user-name">
              {{ profile.first_name }} {{ profile.last_name }}
            </h3>
            <button
              v-if="isViewingOther"
              class="send-message-btn"
              @click="startChat"
            >
              <i class="fa-regular fa-comment-dots"></i> Send Message
            </button>
          </div>

          <a
            v-if="profile.user_email"
            :href="`mailto:${profile.user_email}`"
            class="email-link"
          >
            {{ profile.user_email }}
          </a>

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
        <div class="project-count">
          {{ 10 - myProjects.length }} out of 10 left
        </div>
      </div>

      <div v-for="project in myProjects" :key="project.id" class="project-card">
        <div class="project-header">
          <h3 class="project-title">{{ project.thesis_name }}</h3>
          <!-- Actions for owner -->
          <div class="project-actions" v-if="!isViewingOther">
            <!-- Кнопка -->
            <button
              class="action-btn green"
              title="Send to Dean's Office"
              @click="approveProject(project.id)"
            >
              <img :src="requestIcon" alt="Approve" class="icon" />
            </button>

            <button
              class="action-btn gray"
              title="Edit"
              @click="goToEditProject(project.thesis_id)"
            >
              <i class="fa-solid fa-pen"></i>
            </button>

            <button
              class="action-btn red"
              title="Delete"
              @click="confirmSupervisorDelete(project)"
            >
              <i class="fa-solid fa-trash"></i>
            </button>
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
              :disabled="
                userHasTeam || userHasPendingRequest || isTeamFull(project)
              "
              @click="applyToTeam(project.id)"
            >
              {{
                userHasTeam
                  ? "Already in a team"
                  : userHasPendingRequest
                  ? "Applied"
                  : isTeamFull(project)
                  ? "Team is full"
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
        <div
          v-if="!isViewingOther"
          class="compatibility-text"
          :class="getCompatibilityClass(project.required_skills)"
        >
          Compatibility:
          {{ calculateCompatibility(project.required_skills) }}%
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
    </div>
  </div>
  <!-- ❌ Modal: Cannot Delete (team has members) -->
  <div v-if="showBlockedModal" class="modal-overlay">
    <div class="modal">
      <p>You cannot delete this team while it has members.</p>
      <div class="modal-actions">
        <button class="cancel-btn" @click="showBlockedModal = false">
          Okay
        </button>
      </div>
    </div>
  </div>

  <div v-if="showDeleteModal" class="modal-overlay">
    <div class="modal">
      <p>Are you sure you want to delete this team and its project?</p>
      <div class="modal-actions">
        <button class="cancel-btn" @click="cancelDelete">Cancel</button>
        <button class="confirm-btn" @click="deleteTeam">Yes, Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import requestIcon from "../../../icons/request.png";
import { useAuthStore } from "../../../store/auth";
import { useLikeStore } from "../../../store/likes";
import { useChatStore } from "../../../store/chat";
const chatStore = useChatStore();
const likeStore = useLikeStore();
const userHasTeam = computed(() => authStore.userHasTeam);
const userHasPendingRequest = computed(() => authStore.userHasPendingRequest);
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const profile = ref({});
const showDeleteModal = ref(false);
const showBlockedModal = ref(false);
const teamToDelete = ref(null);
const skills = ref([]);
const selectedSkills = ref([]);
const mySkills = ref([]);
const myProjects = ref([]);
const isViewingOther = computed(() => !!route.params.id);
const isTeamFull = (project) => project?.members?.length >= 4;
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
const confirmSupervisorDelete = (project) => {
  if (project.members && project.members.length > 0) {
    // ❌ Показываем окно, что удаление невозможно
    showBlockedModal.value = true;
  } else {
    // ✅ Показываем окно подтверждения удаления
    showDeleteModal.value = true;
    teamToDelete.value = project.id;
  }
};

const cancelDelete = () => {
  showDeleteModal.value = false;
  teamToDelete.value = null;
};

const deleteTeam = async () => {
  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/teams/${teamToDelete.value}/supervisor-delete/`,
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    alert("Team deleted successfully.");
    myProjects.value = myProjects.value.filter(
      (p) => p.id !== teamToDelete.value
    );
    cancelDelete();
  } catch (err) {
    alert(err.response?.data?.error || "Failed to delete");
  }
};
const approveProject = async (projectId) => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/${projectId}/approve/`,
      {},
      {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      }
    );
    alert("Project successfully approved and sent to dean office!");
  } catch (err) {
    alert(err.response?.data?.error || "Failed to approve");
    console.error(err);
  }
};
const startChat = async () => {
  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/api/chats/start/",
      { user_id: profile.value.user },
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    chatStore.setActiveChat(res.data.id);
    chatStore.openChatModal();
  } catch (err) {
    console.error("Ошибка при создании чата:", err);
    alert("Не удалось начать чат");
  }
};
const goToCreateProject = () => {
  router.push("/create-project");
};
const goToEditProject = (projectId) => {
  router.push({ path: "/create-project", query: { edit: "true", projectId } });
};
const goToEdit = () => {
  router.push({ path: "/profile", query: { edit: "true" } });
};
const getSkillClass = (skillName, project) => {
  const skill = skillName?.toLowerCase?.() || "";
  const mySkillNames = mySkills.value.map((s) => s.name.toLowerCase());

  // 👥 Скиллы, покрытые студентами — только для текущего проекта
  const coveredByStudents = new Set();
  project?.members?.forEach((member) => {
    member.skills?.forEach((s) => {
      if (s.name) coveredByStudents.add(s.name.toLowerCase());
    });
  });

  const isMine = mySkillNames.includes(skill);
  const isStudentCovered = coveredByStudents.has(skill);

  if (!isViewingOther.value) {
    if (isMine && isStudentCovered) return "skill-pill my-covered";
    if (isMine) return "skill-pill my-unique";
    if (isStudentCovered) return "skill-pill covered";
    return "skill-pill";
  }

  if (isMine && isStudentCovered) return "skill-pill my-covered";
  if (isMine) return "skill-pill my-unique";
  if (isStudentCovered) return "skill-pill covered";
  return "skill-pill";
};

const calculateCompatibility = (requiredSkills) => {
  const required = requiredSkills.map((s) =>
    typeof s === "string" ? s.toLowerCase() : s.name?.toLowerCase()
  );

  const mySkillNames = mySkills.value.map((s) =>
    typeof s === "string" ? s.toLowerCase() : s.name?.toLowerCase()
  );

  console.log("🧩 Required skills:", required);
  console.log("🎓 My professor skills:", mySkillNames);

  const matched = required.filter((skill) => mySkillNames.includes(skill));
  console.log("✅ Matched:", matched);

  return Math.round((matched.length / required.length) * 100);
};

const getCompatibilityClass = (skills) => {
  const percent = calculateCompatibility(skills);
  if (percent >= 67) return "compatibility-good";
  if (percent >= 33) return "compatibility-medium";
  return "compatibility-low";
};
onMounted(async () => {
  await likeStore.fetchLikes();

  try {
    const skillsRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/skills/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    skills.value = skillsRes.data;
    if (isViewingOther.value) {
      const me = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      mySkills.value = me.data.skills || [];
    }

    if (isViewingOther.value) {
      const profileRes = await axios.get(
        `http://127.0.0.1:8000/api/profiles/supervisors/${route.params.id}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profile.value.skills?.map((s) => s.id) || [];
      myProjects.value = profile.value.projects || [];
      await authStore.refreshTeamAndRequestStatus();
    } else {
      const profileRes = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profile.value.skills?.map((s) => s.id) || [];
      mySkills.value = profile.value.skills || [];

      const projectsRes = await axios.get(
        "http://127.0.0.1:8000/api/teams/my/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      myProjects.value = Array.isArray(projectsRes.data)
        ? projectsRes.data
        : [projectsRes.data];

      // ✅ Обновляем статус запроса и команды
      await authStore.refreshTeamAndRequestStatus();
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
  max-width: 1100px;
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
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.edit-btn {
  background: #28a745;
  color: white;
}

.edit-btn:hover {
  background: #218838;
}

.create-btn {
  background: #80c5ff;
  color: white;
}

.create-btn:hover {
  background: #5bb1ff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.profile-body {
  display: flex;
  gap: 30px;
  margin-top: 30px;
}

/* .left-column {
  flex: 1;
} */

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
  font-weight: 600;
  margin-top: 0px;
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
  background: #adadad;
  padding: 6px 12px;
  color: white;
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
  margin: 0px;
}
.info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.send-message-btn {
  /* margin-top: 10px; ❌ убрать */
  background: #007bff;
  margin-bottom: 20px;
  color: white;
  padding: 8px 14px; /* уменьшаем чуть-чуть padding */
  border: none;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center; /* для центрирования иконки и текста */
  gap: 8px;
}

.send-message-btn:hover {
  background-color: #0056b3;
}
.heart-icon {
  font-size: 20px;
  color: #ccc;
  margin-right: 10px;
  padding-left: 10px;
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
  white-space: nowrap;
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

.action-btn .icon,
.action-btn i {
  width: 16px;
  height: 16px;
  color: white;
}

.action-btn img.icon {
  object-fit: contain;
}

/* Цвета */
.green {
  background-color: #2ead2b;
}

.gray {
  background-color: #a8a8a8;
}

.red {
  background-color: #c23434;
}
.actions {
  display: flex;
  align-items: center; /* 💥 ключ! */
  gap: 10px;
}
/* Hover (необязательно) */
.action-btn:hover {
  opacity: 0.9;
}

.icon {
  width: 16px;
  height: 16px;
  filter: brightness(0) invert(1);
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
.compatibility-text {
  font-size: 14px;
  font-weight: bold;
}

.compatibility-good {
  color: #28a745;
}
.compatibility-medium {
  color: orange;
}
.compatibility-low {
  color: #dc3545;
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
  border: 3px solid gold !important;
  box-shadow: 0 0 5px rgba(255, 215, 0, 0.8);
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal {
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.modal-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}
.cancel-btn,
.confirm-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
.cancel-btn {
  background: #6c757d;
  color: white;
}
.confirm-btn {
  background: #dc3545;
  color: white;
}
@media (max-width: 768px) {
  .profile-container {
    padding: 30px 20px;
  }

  .profile-body {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .left-column,
  .right-column {
    width: 100%;
  }

  .profile-image {
    width: 120px;
    height: 120px;
    margin-bottom: 20px;
  }

  .projects-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .project-actions,
  .actions {
    align-self: flex-start;
  }

  .team-members {
    flex-wrap: wrap;
    justify-content: center;
  }

  .skills-grid,
  .project-skills {
    justify-content: center;
  }
}
</style>
