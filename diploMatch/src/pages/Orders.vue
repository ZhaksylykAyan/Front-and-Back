<template>
  <div class="orders-container">
    <!-- ===== STUDENT VIEW ===== -->
    <div v-if="userRole === 'Student'">
      <h2 class="section-title">Requests</h2>

      <!-- 💥 Supervisor Request -->
      <div
        v-if="mySupervisorRequest"
        class="request-card"
        style="border-left: 4px solid #007bff"
      >
        <div class="request-header">
          <h3 class="project-title">
            {{ mySupervisorRequest.team.thesis_name }}
          </h3>

          <div class="status-with-button">
            <span
              class="status-tag"
              :class="mySupervisorRequest.status.toLowerCase()"
            >
              {{ mySupervisorRequest.status }}
            </span>

            <button
              v-if="mySupervisorRequest.status === 'pending'"
              class="cancel-btn"
              @click="cancelSupervisorRequest"
            >
              Cancel
            </button>
          </div>
        </div>

        <p class="project-description">
          {{ mySupervisorRequest.team.thesis_description }}
        </p>
        <div class="project-skills">
          <span
            v-for="skill in mySupervisorRequest.team.required_skills"
            :key="skill"
            class="skill-pill"
          >
            {{ skill }}
          </span>
        </div>
      </div>

      <div v-for="req in requests" :key="req.id" class="request-card">
        <div class="request-header">
          <div>
            <h3 class="project-title">{{ req.team.thesis_name }}</h3>
          </div>

          <div class="status-with-button">
            <span class="status-tag" :class="req.status.toLowerCase()">
              {{ req.status }}
            </span>
            <button
              v-if="req.status === 'pending'"
              class="cancel-btn"
              @click="cancelRequest(req.id)"
            >
              Cancel
            </button>
          </div>
        </div>

        <p class="project-description">{{ req.team.thesis_description }}</p>
        <div class="project-skills">
          <span
            v-for="skill in req.team.required_skills"
            :key="skill"
            class="skill-pill"
          >
            {{ skill }}
          </span>
        </div>
      </div>
    </div>

    <!-- ===== SUPERVISOR VIEW ===== -->
    <div v-else-if="userRole === 'Supervisor'">
      <h2 class="section-title">Incoming Supervisor Requests</h2>
      <div v-if="supervisorRequests.length === 0" class="empty-msg">
        No incoming supervisor requests yet.
      </div>

      <div v-for="req in supervisorRequests" :key="req.id" class="request-card">
        <div class="request-header">
          <div>
            <h3 class="project-title">{{ req.team.thesis_name }}</h3>
            <p class="project-description">{{ req.team.thesis_description }}</p>
          </div>
          <div class="owner-actions">
            <button
              v-if="req.status === 'pending'"
              class="accept-btn"
              @click="acceptSupervisorRequest(req.id)"
            >
              ✔
            </button>
            <button
              v-if="req.status === 'pending'"
              class="reject-btn"
              @click="rejectSupervisorRequest(req.id)"
            >
              ✖
            </button>
            <span
              v-if="req.status !== 'pending'"
              class="status-tag"
              :class="req.status.toLowerCase()"
            >
              {{ req.status }}
            </span>
          </div>
        </div>

        <div class="team-members">
          <img
            v-for="member in req.team.members"
            :key="member.user"
            :src="getPhoto(member)"
            :alt="member.first_name"
            class="avatar"
          />
          <span class="member-label">want to add you as their Supervisor</span>
        </div>

        <div class="project-skills">
          <span
            v-for="skill in req.team.required_skills"
            :key="typeof skill === 'object' ? skill.id || skill.name : skill"
            :class="
              getSupervisorSkillClass(skill?.name || skill, req.team.members)
            "
          >
            {{ skill?.name || skill }}
          </span>
        </div>

        <div
          class="compatibility-text"
          :class="
            getCompatibilityClass(req.team.required_skills, req.team.members)
          "
        >
          Compatibility:
          {{ getCompatibility(req.team.required_skills, req.team.members) }}%
        </div>
      </div>
    </div>

    <!-- ===== OWNER VIEW: Incoming Join Requests ===== -->
    <div
      v-if="
        (isOwner || userRole === 'Student') && incomingJoinRequests.length > 0
      "
    >
      <h2 class="section-title">Incoming Join Requests</h2>

      <div
        v-for="req in incomingJoinRequests"
        :key="req.id"
        class="request-card"
      >
        <div class="request-header">
          <h3 class="project-title">
            {{ req.student.first_name }} {{ req.student.last_name }}
          </h3>
          <div class="owner-actions">
            <template v-if="req.status === 'pending'">
              <button
                class="accept-btn"
                @click="acceptJoinRequest(req.team.id, req.student.user, req)"
              >
                ✔
              </button>
              <button
                class="reject-btn"
                @click="rejectJoinRequest(req.team.id, req.student.user, req)"
              >
                ✖
              </button>
            </template>
            <span v-else class="status-tag" :class="req.status.toLowerCase()">
              {{ req.status }}
            </span>
          </div>
        </div>

        <p class="project-description">
          Request to join: {{ req.team.thesis_name }}
        </p>

        <div class="team-members" style="margin-bottom: 10px">
          <a :href="`/students/${req.student.user}`">
            <img
              :src="getPhoto(req.student)"
              :alt="req.student.first_name"
              class="avatar"
              style="cursor: pointer"
            />
          </a>
        </div>

        <div class="skills-grid">
          <span
            v-for="skill in req.student.skills"
            :key="skill.id"
            :class="
              getRequestSkillClass(
                skill.name,
                req.team_members,
                req.team.required_skills
              )
            "
          >
            {{ skill.name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useAuthStore } from "../store/auth";

const authStore = useAuthStore();
const userRole = authStore.user?.role;
const mySkills = ref([]);
const requests = ref([]);
const supervisorRequests = ref([]);
const isOwner = ref(false);
const showSentRequestReminder = ref(false);
const mySupervisorRequest = ref(null);
const incomingJoinRequests = ref([]);

const getPhoto = (member) => {
  if (member.photo) {
    return member.photo.startsWith("http")
      ? member.photo
      : `http://127.0.0.1:8000${member.photo}`;
  }
  return new URL("../icons/default-avatar.png", import.meta.url).href;
};

const fetchRequests = async () => {
  try {
    // ===== Check if user is owner of any team =====
    try {
      const resTeam = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });

      // Если backend возвращает массив команд — проверим owner
      if (Array.isArray(resTeam.data)) {
        isOwner.value = resTeam.data.some(
          (team) => team.owner === authStore.user.id
        );
      } else {
        // Если backend возвращает одну команду
        isOwner.value =
          resTeam.data.owner === authStore.user.id ||
          resTeam.data.is_owner === true;
      }
    } catch (err) {
      isOwner.value = false;
    }

    // ===== Student-specific logic =====
    if (userRole === "Student") {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/teams/my-join-requests/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      requests.value = res.data;

      await fetchMySupervisorRequest();

      if (
        !isOwner.value &&
        localStorage.getItem("lastSupervisorRequestSent") === "true"
      ) {
        showSentRequestReminder.value = true;
      }
    }

    // ===== Supervisor-specific logic =====
    if (userRole === "Supervisor") {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/teams/supervisor-requests/incoming/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      supervisorRequests.value = res.data;
    }

    // ✅ Final: universal for ANY owner (student or supervisor)
    if (isOwner.value) {
      await fetchIncomingJoinRequests();
    }
  } catch (err) {
    console.error("Failed to fetch requests:", err);
  }
};

const fetchMySupervisorRequest = async () => {
  try {
    const res = await axios.get(
      "http://127.0.0.1:8000/api/teams/my-supervisor-request/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    mySupervisorRequest.value = res.data;
  } catch (err) {
    mySupervisorRequest.value = null;
  }
};

const fetchIncomingJoinRequests = async () => {
  try {
    const res = await axios.get(
      "http://127.0.0.1:8000/api/teams/my-team-join-requests/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    incomingJoinRequests.value = res.data;
  } catch (err) {
    incomingJoinRequests.value = [];
  }
};

const cancelSupervisorRequest = async () => {
  try {
    await axios.post(
      "http://127.0.0.1:8000/api/teams/supervisor-requests/cancel/",
      {},
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    mySupervisorRequest.value = null;
    await fetchRequests();
  } catch (err) {
    console.error("Failed to cancel supervisor request", err);
  }
};

const cancelRequest = async (id) => {
  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/teams/my-join-requests/${id}/`,
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    requests.value = requests.value.filter((r) => r.id !== id);

    // ✅ Обнови статус после отмены
    await authStore.refreshTeamAndRequestStatus();
  } catch (err) {
    console.error("Failed to cancel request", err);
  }
};

const acceptSupervisorRequest = async (requestId) => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/supervisor-requests/${requestId}/accept/`,
      {},
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    await fetchRequests();
  } catch (err) {
    console.error("Failed to accept supervisor request", err);
  }
};

const rejectSupervisorRequest = async (requestId) => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/supervisor-requests/${requestId}/reject/`,
      {},
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    await fetchRequests();
  } catch (err) {
    console.error("Failed to reject supervisor request", err);
  }
};

const acceptJoinRequest = async (teamId, studentId, req) => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/${teamId}/join-requests/${studentId}/accept/`,
      {},
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    await fetchRequests();
    req.status = "accepted";
  } catch (err) {
    console.error("Failed to accept join request", err);
  }
};

const rejectJoinRequest = async (teamId, studentId, req) => {
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/teams/${teamId}/join-requests/${studentId}/reject/`,
      {},
      { headers: { Authorization: `Bearer ${authStore.token}` } }
    );
    await fetchRequests();
    req.status = "rejected";
  } catch (err) {
    console.error("Failed to reject join request", err);
  }
};
const getRequestSkillClass = (
  skillName,
  teamMembersSnapshot,
  requiredSkills
) => {
  const skill = skillName?.toLowerCase?.() || "";

  // Приводим required skills в lowercase
  const required = requiredSkills.map((s) => s?.toLowerCase?.() || "");

  // Собираем все скиллы уже принятых участников команды (snapshot на момент заявки)
  const allTeamSkills = new Set();
  teamMembersSnapshot?.forEach((member) => {
    member.skills?.forEach((s) => {
      if (s?.name) {
        allTeamSkills.add(s.name.toLowerCase());
      }
    });
  });

  const isRequired = required.includes(skill);
  const isAlreadyCovered = allTeamSkills.has(skill);

  // 🟩 Полезный и ещё не покрыт
  if (isRequired && !isAlreadyCovered) return "skill-pill my-unique";

  // 🟢 Полезный, но уже покрыт кем-то
  if (isRequired && isAlreadyCovered) return "skill-pill my-covered";

  // 🟦 У него есть этот скилл, но он не нужен
  if (!isRequired) return "skill-pill";

  // 🔵 Просто по умолчанию
  return "skill-pill";
};
const getSupervisorSkillClass = (skillName, teamMembers) => {
  const skill = skillName?.toLowerCase?.() || "";

  // Все скиллы студентов
  const studentSkills = new Set();
  teamMembers.forEach((member) => {
    member.skills?.forEach((s) => {
      if (s.name) studentSkills.add(s.name.toLowerCase());
    });
  });

  // Все твои скиллы
  const professorSkills = mySkills.value.map((s) => s.name.toLowerCase());

  const isCoveredByStudent = studentSkills.has(skill);
  const isCoveredByProfessor = professorSkills.includes(skill);

  if (isCoveredByProfessor && isCoveredByStudent)
    return "skill-pill my-covered"; // 🟢 серо-зеленый
  if (isCoveredByProfessor) return "skill-pill my-unique"; // 🟢 зеленый
  if (isCoveredByStudent) return "skill-pill covered"; // 🟦 серо-синий
  return "skill-pill"; // 🔵 обычный
};

const getCompatibility = (requiredSkills, teamMembers) => {
  const required = requiredSkills
    .map((s) => s.name?.toLowerCase() || s?.toLowerCase())
    .filter(Boolean);

  const professorSkills = new Set(
    mySkills.value.map((s) => s.name.toLowerCase())
  );

  // Считаем сколько required скиллов покрывает профессор
  const coveredByProfessor = required.filter((skill) =>
    professorSkills.has(skill)
  );

  return Math.round((coveredByProfessor.length / required.length) * 100);
};
const getCompatibilityClass = (requiredSkills, teamMembers) => {
  const percent = getCompatibility(requiredSkills, teamMembers);

  if (isNaN(percent)) return "compatibility-na";
  if (percent >= 67) return "compatibility-good";
  if (percent >= 33) return "compatibility-medium";
  return "compatibility-low";
};

onMounted(async () => {
  await fetchRequests();
  const res = await axios.get(
    "http://127.0.0.1:8000/api/profiles/complete-profile/",
    {
      headers: { Authorization: `Bearer ${authStore.token}` },
    }
  );
  mySkills.value = res.data.skills || [];
});
</script>

<style scoped>
.orders-container {
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
.reminder-card {
  background-color: #fff7cc;
  color: #7c5b00;
  padding: 14px 20px;
  border: 1px solid #ffdd88;
  border-radius: 10px;
  margin-bottom: 24px;
  text-align: left;
  font-size: 14px;
}
.request-card {
  background: linear-gradient(145deg, #e6f0fb, #f4f8ff);
  padding: 30px 24px;
  border-radius: 16px;
  margin-bottom: 30px;
  text-align: left;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.project-title {
  font-size: 18px;
  font-weight: bold;
}
.status-with-button {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.status-tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
  text-transform: capitalize;
}
.status-tag.pending {
  border: 2px solid orange;
  color: orange;
}
.status-tag.accepted {
  border: 2px solid #28a745;
  color: #28a745;
}
.status-tag.rejected {
  border: 2px solid #dc3545;
  color: #dc3545;
}
.project-description {
  font-size: 15px;
  color: #444;
  margin-bottom: 4px;
}
.project-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 8px;
}
.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}
.skill-pill {
  background: #80c5ff;
  font-family: Arial, sans-serif, "Segoe UI";
  color: black;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.skill-pill.my-unique {
  background: #83d481;
  color: black;
}

.skill-pill.my-covered {
  background: #9ede9c;
  color: #898787;
}

.skill-pill.covered {
  background: #b1d0e9;
  color: #898787;
}

/* .skill-pill.extra {
  background: #c8e1ff;
  color: #333;
} */
.compatibility-good {
  color: #28a745; /* зелёный */
  font-weight: bold;
}

.compatibility-medium {
  color: #ffc107; /* жёлтый */
  font-weight: bold;
}

.compatibility-low {
  color: #dc3545; /* красный */
  font-weight: bold;
}

.compatibility-na {
  color: #6c757d; /* серый */
}

.cancel-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
}
.cancel-btn:hover {
  background-color: #c82333;
}
.accept-btn,
.reject-btn {
  font-size: 14px;
  font-weight: bold;
  padding: 10px 18px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
}
.accept-btn {
  background-color: #28a745;
  color: white;
}
.reject-btn {
  background-color: #dc3545;
  color: white;
}
.accept-btn:hover {
  background-color: #218838;
}
.reject-btn:hover {
  background-color: #c82333;
}
.owner-actions {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}
.team-members {
  display: flex;
  align-items: center;
  gap: 12px;
}
.team-members .avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid #007bff;
  object-fit: cover;
}
.member-label {
  font-size: 14px;
  color: #555;
}
</style>
