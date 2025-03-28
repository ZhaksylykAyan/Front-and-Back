<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <h2>My Profile</h2>
        <div class="actions" v-if="!props.readonly">
          <button class="edit-btn" @click="goToEdit">✏️ Edit Profile</button>
          <button class="create-btn" @click="goToCreateProject">
            + Create Project
          </button>
        </div>
      </div>

      <div class="profile-main">
        <div class="photo-section">
          <img :src="profileImage" class="profile-img" />
        </div>

        <div class="profile-info">
          <h3>{{ profile.first_name }} {{ profile.last_name }}</h3>
          <a href="#"> {{ profile.user_email }} </a>
          <p><strong>GPA:</strong> {{ profile.gpa }}</p>
          <p v-if="profile.specialization">
            <strong>Major:</strong> {{ profile.specialization }}
          </p>
          <p v-if="profile.portfolio">
            <strong>
              <a :href="profile.portfolio" target="_blank">
                {{ profile.portfolio }}
              </a>
            </strong>
          </p>

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
              :disabled="userHasTeam || userHasPendingRequest"
              @click="applyToTeam(team.id)"
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
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../../../store/auth";
import axios from "axios";
import { useLikeStore } from "../../../store/likes";
const likeStore = useLikeStore();
const router = useRouter();
const authStore = useAuthStore();
const team = ref(null);
const profile = ref({});
const mySkills = ref([]);
const skills = ref([]);
const selectedSkills = ref([]);
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
      const myProfile = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      mySkills.value = myProfile.data.skills || [];
    }

    if (
      props.viewedUserId &&
      props.viewedUserId !== authStore.user.id.toString()
    ) {
      // 📌 Загружаем профиль другого пользователя
      const profileRes = await axios.get(
        `http://127.0.0.1:8000/api/profiles/students/${props.viewedUserId}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];
      userHasTeam.value = profileRes.data?.team !== null;
      await authStore.refreshTeamAndRequestStatus();

      // 📌 Подставляем команду из profileRes
      team.value = profileRes.data.team || null;
    } else {
      // 📌 Загружаем профиль текущего пользователя
      const profileRes = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );

      profile.value = profileRes.data;
      selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];

      // 📌 Только в этом случае запрашиваем api/teams/my/
      const teamRes = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      team.value = teamRes.data || null;
    }
  } catch (err) {
    console.error("Error loading profile or team data:", err);
    team.value = null;
  }
});

const goToEdit = () => {
  if (authStore.user?.role) {
    router.push({ path: "/profile", query: { edit: "true" } });
  }
};

const goToCreateProject = () => {
  router.push("/create-project");
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
  max-width: 1000px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.profile-header h2 {
  font-size: 22px;
  font-weight: bold;
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
  border-radius: 6px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: 0.3s ease;
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
  background: #0056b3;
}

.profile-main {
  display: flex;
  gap: 30px;
  margin-top: 30px;
}

.photo-section {
  flex: 1;
}

.profile-img {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #007bff;
}

.profile-info {
  flex: 2;
}

.profile-info h3 {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 5px;
}

.profile-info p {
  margin-bottom: 6px;
  font-size: 15px;
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

.project-section {
  padding-left: 30px;
  max-width: 1000px;
  width: 100%;
}

.project-card {
  width: 100%;
  background: #e6f0ff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.project-description {
  font-size: 14px;
  margin-bottom: 15px;
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
  border: 2px solid #28a745 !important;
}
.owner-avatar {
  border: 3px solid gold !important;
  box-shadow: 0 0 5px rgba(255, 215, 0, 0.8);
}
.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
