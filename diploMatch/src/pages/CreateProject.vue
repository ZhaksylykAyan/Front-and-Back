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
          required
        />

        <input
          v-model="project.title_kz"
          type="text"
          class="form-input"
          placeholder="Project Title (Kazakh)"
          required
        />

        <input
          v-model="project.title_ru"
          type="text"
          class="form-input"
          placeholder="Project Title (Russian)"
          required
        />

        <textarea
          v-model="project.description"
          class="form-textarea"
          placeholder="Project Description"
          required
        ></textarea>

        <h3 class="skill-title">Choose skills you need:</h3>
        <div class="skills-grid">
          <div
            v-for="skill in allSkills"
            :key="skill.id"
            :class="[
              'skill-card',
              { selected: selectedSkills.includes(skill.id) },
            ]"
            @click="toggleSkill(skill.id)"
          >
            {{ skill.name }}
          </div>
        </div>

        <button type="submit" class="create-btn">
          {{ isEditMode ? "Update" : "Create" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";
import { useRouter, useRoute } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const isEditMode = ref(false);
const allSkills = ref([]);
const selectedSkills = ref([]);
const projectId = ref(null);

const project = ref({
  title: "",
  title_kz: "",
  title_ru: "",
  description: "",
});

// Загрузка скиллов и если редактируем — загрузка данных проекта
onMounted(async () => {
  try {
    const skillsRes = await axios.get("http://127.0.0.1:8000/api/profiles/skills/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    allSkills.value = skillsRes.data;

    if (route.query.edit === "true" && route.query.projectId) {
      isEditMode.value = true;
      projectId.value = route.query.projectId;

      const projectRes = await axios.get(`http://127.0.0.1:8000/api/topics/${projectId.value}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });

      const data = projectRes.data;
      project.value.title = data.title;
      project.value.title_kz = data.title_kz;
      project.value.title_ru = data.title_ru;
      project.value.description = data.description;
      selectedSkills.value = data.required_skills.map((id) => Number(id));
    }
  } catch (err) {
    console.error("Failed to load data", err);
  }
});

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
</style>
