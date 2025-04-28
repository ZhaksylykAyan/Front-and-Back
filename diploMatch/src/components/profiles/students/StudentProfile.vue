<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <h2 v-if="!isViewingOther">{{ "My Profile" }}</h2>
        <div class="actions">
          <button v-if="!isViewingOther" class="edit-btn" @click="goToEdit">
            <i class="fa-solid fa-pen" style="margin-right: 6px"></i>
            Edit Profile
          </button>

          <button
            v-if="!isViewingOther"
            class="create-btn"
            @click="goToCreateProject"
          >
            <i class="fa-solid fa-plus"></i>
            Create Project
          </button>
        </div>
      </div>

      <div class="profile-main">
        <div class="photo-section">
          <img :src="profileImage" class="profile-img" />
        </div>

        <div class="profile-info">
          <div class="info-header">
            <div class="name-box">
              <h3>{{ profile.first_name }} {{ profile.last_name }}</h3>
              <a
                v-if="profile.user_email"
                :href="`mailto:${profile.user_email}`"
                class="email-link"
              >
                {{ profile.user_email }}
              </a>
            </div>
            <button
              v-if="isViewingOther"
              class="send-message-btn"
              @click="startChat"
            >
              <i class="fa-regular fa-comment-dots"></i> Send Message
            </button>
          </div>
          <p><strong>GPA:</strong> {{ profile.gpa }}</p>
          <p v-if="profile.specialization">
            <strong>Major:</strong> {{ profile.specialization }}
          </p>
          <div v-if="profile.portfolio" class="portfolio-link">
            <a :href="profile.portfolio" target="_blank" rel="noopener">
              {{ profile.portfolio }}
            </a>
          </div>

          <div class="section-title">Skills</div>
          <div class="skills-box">
            <span
              v-for="skill in selectedSkillsNames"
              :key="skill"
              class="skill-pill"
            >
              {{ skill }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 💡 My Project -->
    <div v-if="team && team.thesis_topic" class="project-section">
      <h2>{{ isViewingOther ? "Projects" : "My Projects" }}</h2>
      <div class="project-card">
        <div class="project-header">
          <h3 class="project-title">{{ team.thesis_name }}</h3>
          <div v-if="isViewingOther" class="actions">
            <i
              :class="[
                'heart-icon',
                likeStore.likedProjectIds.includes(team.id)
                  ? 'fa-solid fa-heart'
                  : 'fa-regular fa-heart',
              ]"
              @click="toggleLike(team.id)"
              title="Add to favorites"
            ></i>
            <button
              class="apply-btn"
              v-if="isViewingOther && !isViewedSupervisor"
              :disabled="userHasTeam || userHasPendingRequest || isTeamFull"
              @click="applyToTeam(team.id)"
            >
              {{
                isTeamFull
                  ? "Team is full"
                  : userHasTeam
                  ? "Already in a team"
                  : userHasPendingRequest
                  ? "Applied"
                  : "Apply"
              }}
            </button>
          </div>
          <div
            class="project-actions"
            v-if="
              !isViewingOther &&
              (isOwnerOfTeam || authStore.user?.role === 'Student')
            "
          >
            <!-- Кнопка Edit только для owner'а -->
            <button
              v-if="isOwnerOfTeam"
              class="action-btn gray"
              title="Edit Project"
              @click="editProject"
            >
              <i class="fa-solid fa-pen"></i>
            </button>

            <!-- Кнопка Leave только для студентов -->
            <button
              v-if="authStore.user?.role === 'Student'"
              class="action-btn red"
              title="Leave team"
              @click="leaveTeam"
            >
              <i class="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        </div>
        <p class="project-description">{{ team.thesis_description }}</p>
        <div class="team-members">
          <!-- ✅ Supervisor first -->
          <router-link
            v-if="team.supervisor"
            :to="`/supervisors/${team.supervisor.id}`"
            :title="`${team.supervisor.first_name} ${team.supervisor.last_name} (Supervisor)`"
          >
            <img
              :src="getPhoto(team.supervisor)"
              class="avatar supervisor-avatar"
              alt="Supervisor"
            />
          </router-link>

          <!-- 👥 Members -->
          <router-link
            v-for="member in team.members"
            :key="member.id"
            :to="`/students/${member.user}`"
            :title="member.first_name + ' ' + member.last_name"
          >
            <img
              :src="getPhoto(member)"
              class="avatar"
              :class="{ 'owner-avatar': member.user === team.owner }"
              :alt="member.first_name"
            />
          </router-link>
        </div>

        <div class="project-skills">
          <span
            v-for="skill in team.required_skills"
            :key="skill.id"
            :class="getSkillClass(skill, team)"
          >
            {{ skill }}
          </span>
        </div>
      </div>
    </div>
  </div>
  <div v-if="showLeaveConfirm" class="modal-overlay">
    <div class="modal-box">
      <p>Are you sure you want to leave the team?</p>
      <div class="modal-actions">
        <button @click="confirmLeave" class="confirm-btn">Yes</button>
        <button @click="cancelLeave" class="cancel-btn">No</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../../../store/auth";
import axios from "axios";
import { useLikeStore } from "../../../store/likes";
import { useChatStore } from "../../../store/chat";
const chatStore = useChatStore();
const likeStore = useLikeStore();
const isViewedSupervisor = computed(() => {
  return isViewingOther.value && authStore.user?.role === "Supervisor";
});
const router = useRouter();
const authStore = useAuthStore();
const team = ref(null);
const profile = ref({});
const mySkills = ref([]);
const skills = ref([]);
const selectedSkills = ref([]);
const showLeaveConfirm = ref(false);
const isTeamFull = computed(() => {
  return team.value?.members?.length >= 4;
});
const defaultAvatar = new URL(
  "../../../icons/default-avatar.png",
  import.meta.url
).href;
const route = useRoute();
const props = defineProps({
  readonly: Boolean,
  viewedUserId: String,
});
const userHasTeam = computed(() => authStore.userHasTeam);
const userHasPendingRequest = computed(() => authStore.userHasPendingRequest);
const toggleLike = async (projectId) => {
  await likeStore.toggleLike(projectId);
};
const isOwnerOfTeam = computed(() => {
  return team.value?.owner === authStore.user?.id && !isViewingOther.value;
});
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
const leaveTeam = () => {
  showLeaveConfirm.value = true;
};

const cancelLeave = () => {
  showLeaveConfirm.value = false;
};

const startChat = async () => {
  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/api/chats/start/",
      { user_id: profile.value.user }, // 👈 ВАЖНО: именно user, не id!
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    // Открыть чат с этим пользователем
    chatStore.setActiveChat(res.data.id);
    chatStore.openChatModal();
  } catch (err) {
    console.error("Ошибка при создании чата:", err);
    alert("Не удалось начать чат");
  }
};

const confirmLeave = async () => {
  try {
    await axios.post(
      "http://127.0.0.1:8000/api/teams/leave/",
      {},
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    alert("You left the team.");
    router.go(); // обновить страницу
  } catch (err) {
    console.error("Failed to leave team:", err);
    alert("Failed to leave the team.");
  } finally {
    showLeaveConfirm.value = false;
  }
};
// Если открываем чужой профиль — загружаем профиль этого пользователя
const isViewingOther = computed(
  () =>
    props.viewedUserId && props.viewedUserId !== authStore.user.id.toString()
);

const profileImage = computed(() =>
  profile.value.photo
    ? profile.value.photo.startsWith("http")
      ? profile.value.photo
      : `http://127.0.0.1:8000${profile.value.photo}`
    : defaultAvatar
);

const selectedSkillsNames = computed(() =>
  skills.value
    .filter((skill) => selectedSkills.value.includes(skill.id))
    .map((s) => s.name)
);

const getPhoto = (user) => {
  if (user.photo) {
    return user.photo.startsWith("http")
      ? user.photo
      : `http://127.0.0.1:8000${user.photo}`;
  }
  return defaultAvatar;
};

const getSkillClass = (skillName) => {
  const mySkillNames = mySkills.value
    .filter((s) => s && s.name) // добавим проверку
    .map((s) => s.name.toLowerCase());

  const skill = skillName?.toLowerCase?.() || "";

  const isMySkill = mySkillNames.includes(skill);
  const isCovered = team.value?.members?.some((member) =>
    member.skills?.some((s) => s.name?.toLowerCase() === skill)
  );

  if (isMySkill && isCovered) return "skill-pill my-covered";
  if (isMySkill) return "skill-pill my-unique";
  if (isCovered) return "skill-pill covered";
  return "skill-pill";
};

watch(
  () => route.params.id,
  async (newId, oldId) => {
    if (newId !== oldId) {
      await loadProfileData(); // перезагружаем профиль
    }
  }
);
const loadProfileData = async () => {
  await likeStore.fetchLikes();
  try {
    const skillsRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/skills/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    skills.value = skillsRes.data;

    if (
      props.viewedUserId &&
      props.viewedUserId !== authStore.user.id.toString()
    ) {
      const profileRes = await axios.get(
        `http://127.0.0.1:8000/api/profiles/students/${props.viewedUserId}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];
      team.value = profileRes.data.team || null;
    } else {
      const profileRes = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];

      const teamRes = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      team.value = teamRes.data || null;
    }
  } catch (err) {
    console.error("Error loading profile or team data:", err);
    team.value = null;
  }
};

onMounted(loadProfileData);

const goToEdit = () => {
  if (authStore.user?.role) {
    router.push({ path: "/profile", query: { edit: "true" } });
  }
};

const goToCreateProject = () => {
  router.push("/create-project");
};
const editProject = () => {
  router.push({
    path: "/create-project",
    query: {
      edit: "true",
      projectId: team.value?.thesis_topic?.id,
    },
  });
};
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
}

.profile-header h2 {
  font-size: 22px;
  font-weight: bold;
}
.info-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 10px;
  gap: 20px;
}
.name-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.name-box h3 {
  font-size: 26px;
  font-weight: bold;
  margin: 0;
}

.email-link {
  margin-top: 6px;
  font-size: 15px;
  color: #007bff;
  text-decoration: underline;
}

.info-header h3 {
  font-size: 26px;
  font-weight: bold;
  margin: 0;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.heart-icon {
  font-size: 20px;
  color: #ccc;
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
  white-space: nowrap;
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

.actions button {
  margin-left: 10px;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: 0.3s ease;
}

.edit-btn {
  background: #28a745;
  color: white;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-btn:hover {
  background: #218838;
}

.edit-icon {
  font-size: 14px;
  transition: transform 0.3s ease, color 0.3s ease;
}

/* Анимация при наведении на кнопку */
.edit-btn:hover .edit-icon {
  transform: rotate(-5deg) scale(1.1);
  color: #fffacd; /* мягкий желтоватый оттенок */
}

.create-btn {
  background: #80c5ff;
  color: white;
}

.create-btn:hover {
  background-color: #5bb1ff; /* немного темнее/насыщеннее */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* мягкая тень */
}

.profile-main {
  display: flex;
  gap: 30px;
  margin-top: 30px;
}

.profile-img {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #007bff;
}

.profile-info h3 {
  font-size: 26px;
  font-weight: bold;
  margin-top: 0px;
}

.profile-info p {
  margin-bottom: 6px;
  font-size: 16px;
}

.section-title {
  margin-top: 16px;
  font-weight: 600;
  font-size: 16px;
}

.skills-box {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.skill-pill {
  background: #80c5ff;
  color: black;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
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

.project-section {
  padding-left: 30px;
  max-width: 1100px;
  margin-bottom: 16px;
  width: 100%;
}
.project-section h2 {
  margin-bottom: 30px;
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

.project-description {
  font-size: 15px;
  margin-bottom: 15px;
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

.action-btn i {
  color: white;
}

.action-btn.gray {
  background-color: #a8a8a8;
}
.action-btn.red {
  background-color: #c23434;
}
.team-members {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.team-members a {
  display: inline-block;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.team-members a:hover {
  transform: scale(1.05);
}

.avatar {
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
.owner-avatar {
  border: 2px solid #28a745 !important;
}
.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.confirm-btn {
  background: #c23434;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.cancel-btn {
  background: #ccc;
  color: black;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}
.send-message-btn {
  margin-bottom: 20px;
  background: #007bff;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  margin-left: 400px;
}
.send-message-btn:hover {
  background-color: #0056b3;
}

@media (max-width: 768px) {
  .profile-main {
    flex-direction: column;
    align-items: center;
  }
  .portfolio-link {
    word-break: break-word;
    margin-top: 10px;
    font-size: 14px;
    line-height: 1.4;
    max-width: 100%;
  }

  .portfolio-link a {
    color: #007bff;
    text-decoration: underline;
    word-break: break-all;
  }

  .photo-section,
  .profile-info {
    width: 100%;
    text-align: center;
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .actions {
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px;
  }

  .actions button,
  .actions i {
    width: 100%;
    text-align: center;
  }
  .project-skills {
    justify-content: center;
  }
  .skill-pill {
    word-break: break-word;
    text-align: center;
  }
  .team-members {
    flex-wrap: wrap;
    justify-content: center;
  }

  .profile-container {
    padding: 20px 10px;
  }

  .skills-box {
    justify-content: center;
  }
}
</style>
