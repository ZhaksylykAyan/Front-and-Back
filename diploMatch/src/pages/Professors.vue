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
          <div>
            <strong>{{ prof.first_name }} {{ prof.last_name }}</strong
            ><br />
            <span v-if="prof.degree">{{ prof.degree }}</span
            ><br />
            <small>Compatibility: {{ prof.compatibility || "N/A" }}%</small>
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
        <span v-for="skill in prof.skills" :key="skill.id" class="skill-pill">
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
const isSupervisor = computed(() => authStore.user?.role === "Supervisor");
const isOwner = ref(false);
const defaultAvatar = new URL("../icons/default-avatar.png", import.meta.url)
  .href;

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

    // 💡 Проверка на массив или объект
    if (Array.isArray(res.data)) {
      isOwner.value = res.data.some((team) => team.owner === authStore.user.id);
    } else {
      isOwner.value =
        res.data.is_owner === true || res.data.owner === authStore.user.id;
    }
  } catch (err) {
    isOwner.value = false;
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
  background-color: #007bff;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}

.request-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s ease;
}

.request-btn:hover {
  background-color: #0056b3;
}
</style>
