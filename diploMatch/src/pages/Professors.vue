<template>
  <div class="professors-container">
    <h2 class="section-title">Supervisors</h2>

    <div v-if="professors.length === 0" class="empty-msg">
      No supervisors available.
    </div>

    <div v-for="prof in professors" :key="prof.id" class="professor-card">
      <div class="professor-info">
        <div class="professor-main">
          <router-link :to="`/supervisors/${prof.user}`" class="avatar-link">
            <img :src="getPhoto(prof)" class="avatar" :alt="prof.first_name" />
          </router-link>

          <div class="text-info">
            <div class="name-degree">
              <strong>{{ prof.first_name }} {{ prof.last_name }}</strong
              ><br />
              <span v-if="prof.degree" class="degree">{{ prof.degree }}</span>
            </div>
            <small :class="getCompatibilityClass(prof.skills)">
              Compatibility: {{ calculateCompatibility(prof.skills) }}
            </small>
          </div>
        </div>

        <!-- ✅ Request button внутри info-блока справа -->
        <button
          v-if="isOwner && !isSupervisor"
          class="request-btn"
          @click="sendRequest(prof.user)"
        >
          Request
        </button>
      </div>

      <div class="skills">
        <span
          v-for="skill in prof.skills"
          :key="skill.id"
          :class="getSkillColorClass(skill.name)"
        >
          {{ skill.name }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";

const authStore = useAuthStore();
const professors = ref([]);
const myProjectSkills = ref([]);
const isSupervisor = computed(() => authStore.user?.role === "Supervisor");
const isOwner = ref(false);
const defaultAvatar = new URL("../icons/default-avatar.png", import.meta.url)
  .href;

const calculateCompatibility = (professorSkills) => {
  if (!myProjectSkills.value.length) return "N/A";

  const profSkills = professorSkills.map((s) => s.name?.toLowerCase?.() || "");
  const common = myProjectSkills.value.filter((skill) =>
    profSkills.includes(skill)
  );
  const percent = (common.length / myProjectSkills.value.length) * 100;

  return `${Math.round(percent)}%`;
};
const getCompatibilityClass = (skills) => {
  const percentStr = calculateCompatibility(skills);
  const percent = parseInt(percentStr);

  if (isNaN(percent)) return "compatibility-na";
  if (percent >= 67) return "compatibility-good";
  if (percent >= 33) return "compatibility-medium";
  return "compatibility-low";
};
const getSkillColorClass = (skill) => {
  const normalized = skill.toLowerCase();
  return myProjectSkills.value.includes(normalized)
    ? "skill-pill match"
    : "skill-pill";
};

// Получить список супервизоров с фильтрацией по is_profile_completed
const fetchProfessors = async () => {
  try {
    const res = await axios.get(
      "http://127.0.0.1:8000/api/profiles/supervisors/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );

    professors.value = res.data.filter(
      (prof) => prof.is_profile_completed === true
    );
  } catch (err) {
    console.error("Failed to load professors:", err);
  }
};

// Проверить, является ли текущий пользователь owner команды
const fetchTeamData = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });

    let teamData = res.data;
    if (Array.isArray(teamData)) {
      teamData = teamData.find((team) => team.owner === authStore.user.id);
    }

    if (teamData) {
      isOwner.value = teamData.owner === authStore.user.id;
      myProjectSkills.value = teamData.required_skills.map((s) =>
        s.toLowerCase()
      );
    }
  } catch (err) {
    isOwner.value = false;
    myProjectSkills.value = [];
  }
};

const getPhoto = (prof) => {
  if (prof.photo) {
    return prof.photo.startsWith("http")
      ? prof.photo
      : `http://127.0.0.1:8000${prof.photo}`;
  }
  return defaultAvatar;
};

const sendRequest = async (supervisorId) => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/supervisor-request/${supervisorId}/`,
      {},
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    alert("Request sent to supervisor!");
  } catch (err) {
    console.error("Failed to send request:", err);
    alert("Failed to send request.");
  }
};

onMounted(async () => {
  await fetchTeamData();
  await fetchProfessors();
});
</script>

<style scoped>
.professors-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  text-align: center;
}
.professor-main {
  display: flex;
  align-items: center;
  gap: 20px;
}

.text-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.name-degree {
  line-height: 1.2;
}

.section-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
}

.empty-msg {
  font-size: 16px;
  color: #666;
  margin-top: 40px;
}

.professor-card {
  background: #eef4fb;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
  text-align: left;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.professor-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.degree {
  display: inline-block;
  margin-top: 4px; /* или padding-top */
}

.avatar-link {
  display: inline-block;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.avatar-link:hover {
  transform: scale(1.05);
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}

.skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.skill-pill {
  background-color: #80c5ff;
  color: black;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}

.skill-pill.match {
  background-color: #83d481;
  color: black;
}

.request-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s ease;
}
.compatibility-good {
  color: #2ead2b; /* зелёный */
  font-weight: 600;
}

.compatibility-medium {
  color: #e6a800; /* оранжевый */
  font-weight: 600;
}

.compatibility-low {
  color: #d62d2d; /* красный */
  font-weight: 600;
}

.compatibility-na {
  color: #888;
}

.request-btn:hover {
  background-color: #0056b3;
}
</style>
