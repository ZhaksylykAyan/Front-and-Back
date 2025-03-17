<template>
  <div class="project-container">
    <div class="project-card">
      <h2>Create New Project</h2>

      <form @submit.prevent="submitProject">
        <input
          v-model="project.title"
          type="text"
          class="form-input"
          placeholder="Project Title"
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

        <button type="submit" class="create-btn">Create</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const project = ref({
  title: "",
  description: "",
});

const allSkills = ref([]);
const selectedSkills = ref([]);

// Загрузка всех скиллов
onMounted(async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/profiles/skills/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    allSkills.value = res.data;
  } catch (err) {
    console.error("Failed to load skills", err);
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

  try {
    await axios.post(
      "http://127.0.0.1:8000/api/topics/create/",
      {
        title: project.value.title,
        description: project.value.description,
        required_skills: selectedSkills.value,
      },
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    router.push("/profile");
  } catch (err) {
    console.error("Failed to create project", err.response?.data || err);
    alert("Failed to create project");
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
