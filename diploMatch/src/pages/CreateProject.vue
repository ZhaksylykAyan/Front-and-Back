<template>
  <div class="project-container">
    <div class="project-card">
      <h2>Create New Project</h2>

      <form @submit.prevent="submitProject">
        <input
          v-model="project.title"
          type="text"
          class="form-input"
          placeholder="Project Title (English)"
          :readonly="isDean"
          required
        />

        <input
          v-model="project.title_kz"
          type="text"
          class="form-input"
          placeholder="Project Title (Kazakh)"
          :readonly="isDean"
          required
        />

        <input
          v-model="project.title_ru"
          type="text"
          class="form-input"
          placeholder="Project Title (Russian)"
          :readonly="isDean"
          required
        />

        <textarea
          v-model="project.description"
          class="form-textarea"
          placeholder="Project Description"
          :readonly="isDean"
          required
        ></textarea>
        <div v-if="!isDean">
          <h3 class="skill-title">Choose skills you need:</h3>
          <div class="skills-grid">
            <div
              v-for="skill in allSkills"
              :key="skill.id"
              :readonly="isDean"
              :class="[
                'skill-card',
                { selected: selectedSkills.includes(skill.id) },
              ]"
              @click="toggleSkill(skill.id)"
            >
              {{ skill.name }}
            </div>
          </div>
        </div>
        <button type="submit" class="create-btn" v-if="!isDean">
          {{ isEditMode ? "Update" : "Create" }}
        </button>
      </form>
      <div v-if="isEditMode && teamMembers.length" class="team-members-section">
        <h3>Team Members</h3>
        <ul class="member-list">
          <li
            v-for="member in teamMembers"
            :key="member.user"
            class="member-item"
          >
            <router-link
              :to="`/students/${member.user}`"
              class="member-info"
              title="View profile"
            >
              <img :src="getPhoto(member)" alt="Avatar" class="member-avatar" />
              <span class="member-name">
                {{ member.first_name }} {{ member.last_name }}
              </span>
            </router-link>

            <button
              v-if="(isDean || isOwner || isSupervisor) && member.user !== currentUser.id"
              class="remove-btn"
              @click="confirmRemoveMember(member)"
            >
              🗑 Remove
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
  <div v-if="showRemoveModal" class="modal-overlay">
    <div class="modal">
      <p>Are you sure you want to remove {{ memberToRemove.first_name }}?</p>
      <div class="modal-actions">
        <button class="cancel-btn" @click="showRemoveModal = false">No</button>
        <button class="confirm-btn" @click="removeMember">Yes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";
import { useRouter, useRoute } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const team = ref(null);
const teamMembers = ref([]);
const showRemoveModal = ref(false);
const memberToRemove = ref(null);
const isEditMode = ref(false);
const currentUser = authStore.user;
const isOwner = ref(false);
const isDean = computed(() => currentUser?.role === "Dean Office");
const projectOwnerId = ref(null);
const isSupervisor = ref(currentUser?.role === "Supervisor");
const allSkills = ref([]);
const selectedSkills = ref([]);
const projectId = ref(null);
const getPhoto = (member) => {
  const photo = member.photo || member.user?.photo;
  if (!photo) {
    return new URL("../icons/default-avatar.png", import.meta.url).href;
  }
  return photo.startsWith("http") ? photo : `http://127.0.0.1:8000${photo}`;
};
const project = ref({
  title: "",
  title_kz: "",
  title_ru: "",
  description: "",
});

const loadTeam = async (topicId) => {
  try {
    let endpoint = "http://127.0.0.1:8000/api/teams/my/";
    let response = null;
    let teamData = null;

    if (isDean.value) {
      // 👨‍🎓 Dean → получаем все команды и ищем по topicId
      response = await axios.get("http://127.0.0.1:8000/api/teams/approved/", {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });

      teamData = response.data.find(
        (team) => team.thesis_topic?.id === Number(topicId)
      );
    } else {
      // 👤 Supervisor, Student, Owner → как раньше
      response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });

      if (Array.isArray(response.data)) {
        teamData = response.data.find(
          (team) => team.thesis_topic?.id === Number(topicId)
        );
      } else {
        teamData = response.data;
      }
    }

    if (teamData) {
      team.value = teamData;

      const isCurrentUserStudent =
        currentUser?.role?.toLowerCase() === "student";
      const filteredMembers = isCurrentUserStudent
        ? teamData.members.filter((m) => m.user !== currentUser.id)
        : teamData.members;

      teamMembers.value = filteredMembers;
      isOwner.value = teamData.is_owner ?? false;

      console.log("✅ Team loaded:", team.value);
    } else {
      console.warn("⚠️ No matching team found for topic:", topicId);
    }
  } catch (err) {
    console.error("❌ Error loading team:", err);
  }
};


const confirmRemoveMember = (member) => {
  console.log("Selected member:", member);
  memberToRemove.value = member;
  showRemoveModal.value = true;
};

const removeMember = async () => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/${team.value.id}/remove-member/${memberToRemove.value.user}/`,
      {},
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    // Обновляем список участников
    teamMembers.value = teamMembers.value.filter(
      (m) => m.user !== memberToRemove.value.user
    );
    showRemoveModal.value = false;
    alert("Member removed successfully.");
  } catch (err) {
    console.error("Remove failed:", err);
    alert("Failed to remove member.");
  }
};
// Загрузка скиллов и если редактируем — загрузка данных проекта

// Выбор скиллов
const toggleSkill = (id) => {
  if (selectedSkills.value.includes(id)) {
    selectedSkills.value = selectedSkills.value.filter((s) => s !== id);
  } else {
    if (selectedSkills.value.length >= 10) {
      alert("You can select up to 10 skills only.");
      return;
    }
    selectedSkills.value.push(id);
  }
};

// Отправка проекта
const submitProject = async () => {
  if (
    project.value.title.trim() === "" ||
    project.value.description.trim() === "" ||
    selectedSkills.value.length === 0
  ) {
    alert("All fields are required and at least 1 skill must be selected.");
    return;
  }

  const payload = {
    title: project.value.title,
    title_kz: project.value.title_kz,
    title_ru: project.value.title_ru,
    description: project.value.description,
    required_skills: selectedSkills.value,
  };

  try {
    if (isEditMode.value && projectId.value) {
      // Редактирование (PATCH)
      await axios.patch(
        `http://127.0.0.1:8000/api/topics/${projectId.value}/edit/`,
        payload,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      alert("Project updated!");
    } else {
      // Создание (POST)
      await axios.post("http://127.0.0.1:8000/api/topics/create/", payload, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      alert("Project created!");
    }

    router.push("/profile");
  } catch (err) {
    console.error("Failed to submit project", err.response?.data || err);
    alert("Failed to submit project");
  }
};
onMounted(async () => {
  try {
    const skillsRes = await axios.get(
      "http://127.0.0.1:8000/api/profiles/skills/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    allSkills.value = skillsRes.data;

    if (route.query.edit === "true" && route.query.projectId) {
      isEditMode.value = true;
      projectId.value = route.query.projectId;

      const projectRes = await axios.get(
        `http://127.0.0.1:8000/api/topics/${projectId.value}/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );

      const data = projectRes.data;
      project.value.title = data.title;
      project.value.title_kz = data.title_kz;
      project.value.title_ru = data.title_ru;
      project.value.description = data.description;
      selectedSkills.value = data.required_skills.map((id) => Number(id));
      projectOwnerId.value = data.owner || null;
      isOwner.value = data.is_owner;

      await loadTeam(projectId.value);
      console.log("Team members loaded:", teamMembers.value);
    }
  } catch (err) {
    console.error("Failed to load data", err);
  }
});
</script>

<style scoped>
.project-container {
  display: flex;
  justify-content: center;
  padding: 60px 40px;
}

.project-card {
  background: #eef5fb;
  padding: 30px;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

h2 {
  font-weight: bold;
  margin-bottom: 20px;
  font-size: 22px;
  text-align: center;
}

.form-input,
.form-textarea {
  width: 100%;
  margin-bottom: 15px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
  resize: none;
}

.form-textarea {
  height: 100px;
}

.skill-title {
  font-weight: bold;
  margin: 10px 0;
  font-size: 16px;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.skill-card {
  padding: 6px 14px;
  background: #f0f0f0;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: 0.3s ease;
}

.skill-card:hover {
  background-color: #d6eaff;
}

.skill-card.selected {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}

.create-btn {
  width: 100%;
  background: #007bff;
  color: white;
  font-weight: bold;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.3s ease;
}

.create-btn:hover {
  background: #0056b3;
}
.team-members-section {
  margin-top: 30px;
}
.member-list {
  list-style: none;
  padding: 0;
}
.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 10px;
}
.member-info {
  display: flex;
  align-items: center;
  text-decoration: none;
  gap: 12px;
  color: #333;
}

.member-info:hover .member-name {
  text-decoration: underline;
}

.member-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}

.member-name {
  font-weight: 500;
  font-size: 18px;
}

.remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.remove-btn:hover {
  background: #b02a37;
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
</style>
