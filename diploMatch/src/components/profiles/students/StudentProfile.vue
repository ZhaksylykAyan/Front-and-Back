<!-- src/components/profiles/Students/StudentProfile.vue -->
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
          <p>
            GPA: <strong> {{ profile.gpa }} </strong>
          </p>
          <p v-if="profile.specialization">
            <strong> Specialization: </strong> {{ profile.specialization }}
          </p>
          <p v-if="profile.portfolio">
            <strong>
              <a :href="profile.portfolio" target="_blank">{{
                profile.portfolio
              }}</a>
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
    <div v-if="team && team.thesis_topic" class="project-section">
      <h2 class="section-title">My Project</h2>
      <div class="project-card">
        <h3 class="project-title">{{ team.thesis_name }}</h3>
        <p class="project-description">{{ team.thesis_description }}</p>

        <div class="team-members">
          <router-link
            v-for="member in team.members"
            :key="member.id"
            :to="`/students/${member.user}`"
            :title="member.first_name + ' ' + member.last_name"
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
            v-for="skill in team.required_skills"
            :key="skill.id"
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
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../../../store/auth";
import axios from "axios";

const router = useRouter();
const authStore = useAuthStore();
const team = ref(null);
const profile = ref({});
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

onMounted(async () => {
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
    } else {
      const profileRes = await axios.get(
        "http://127.0.0.1:8000/api/profiles/complete-profile/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      profile.value = profileRes.data;
      selectedSkills.value = profileRes.data.skills?.map((s) => s.id) || [];
    }
    // ✅ Получаем данные о проекте/команде
    const res = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    team.value = res.data;
    console.log("TEAM DATA:", team.value);
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
  padding-top: 20px;
}

.profile-card {
  padding: 30px;
  border-radius: 12px;
  width: 700px;
  max-width: 100%;
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
  background: #007bff;
  color: white;
}

.create-btn:hover {
  background: #0056b3;
}

.profile-main {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.photo-section {
  flex-shrink: 0;
}

.profile-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}

.profile-info {
  flex-grow: 1;
}

.profile-info h3 {
  font-size: 20px;
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
  background: #007bff;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.project-section {
  padding-left: 30px;
  width: 100%;
}

.project-card {
  max-width: 700px;
  width: 100%;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}

.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-pill {
  background-color: #007bff;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
}
</style>
