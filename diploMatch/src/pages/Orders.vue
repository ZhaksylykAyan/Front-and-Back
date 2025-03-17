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
          <h3 class="project-title">{{ mySupervisorRequest.team.thesis_name }}</h3>
          <span class="status-tag" :class="mySupervisorRequest.status.toLowerCase()">
            {{ mySupervisorRequest.status }}
          </span>
        </div>
        <p class="project-description">{{ mySupervisorRequest.team.thesis_description }}</p>
        <div class="project-skills">
          <span
            v-for="skill in mySupervisorRequest.team.required_skills"
            :key="skill"
            class="skill-pill"
          >
            {{ skill }}
          </span>
        </div>
        <button
          v-if="mySupervisorRequest.status === 'pending'"
          class="cancel-btn"
          @click="cancelSupervisorRequest"
        >
          Cancel Request
        </button>
      </div>

      <div v-for="req in requests" :key="req.id" class="request-card">
        <div class="request-header">
          <h3 class="project-title">{{ req.team.thesis_name }}</h3>
          <span class="status-tag" :class="req.status.toLowerCase()">{{ req.status }}</span>
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
        <button
          v-if="req.status === 'pending'"
          class="cancel-btn"
          @click="cancelRequest(req.id)"
        >
          Cancel Request
        </button>
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
            <button v-if="req.status === 'pending'" class="accept-btn" @click="acceptSupervisorRequest(req.id)">✔</button>
            <button v-if="req.status === 'pending'" class="reject-btn" @click="rejectSupervisorRequest(req.id)">✖</button>
            <span v-if="req.status !== 'pending'" class="status-tag" :class="req.status.toLowerCase()">
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
            :key="skill"
            class="skill-pill"
          >
            {{ skill }}
          </span>
        </div>
      </div>
    </div>

    <!-- ===== OWNER VIEW: Incoming Join Requests ===== -->
    <div v-if="isOwner && incomingJoinRequests.length > 0">
      <h2 class="section-title">Incoming Join Requests</h2>

      <div v-for="req in incomingJoinRequests" :key="req.id" class="request-card">
        <div class="request-header">
          <h3 class="project-title">
            {{ req.student.first_name }} {{ req.student.last_name }}
          </h3>
          <div class="owner-actions">
            <template v-if="req.status === 'pending'">
              <button class="accept-btn" @click="acceptJoinRequest(req.team.id, req.student.user, req)">✔</button>
              <button class="reject-btn" @click="rejectJoinRequest(req.team.id, req.student.user, req)">✖</button>
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

        <div class="project-skills">
          <span
            v-for="skill in req.student.skills"
            :key="skill.id"
            class="skill-pill"
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
    // Owner check
    try {
      const resTeam = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      isOwner.value = resTeam.data.is_owner === true;
    } catch (err) {
      isOwner.value = false;
    }

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

    if (userRole === "Supervisor") {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/teams/supervisor-requests/incoming/",
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );
      supervisorRequests.value = res.data;
    }

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
    req.status = "rejected";
  } catch (err) {
    console.error("Failed to reject join request", err);
  }
};

onMounted(() => {
  fetchRequests();
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
.status-tag {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: bold;
  text-transform: capitalize;
}
.status-tag.pending {
  background-color: orange;
  color: white;
}
.status-tag.accepted {
  background-color: #28a745;
  color: white;
}
.status-tag.rejected {
  background-color: #dc3545;
  color: white;
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
.skill-pill {
  background-color: #007bff;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}
.cancel-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
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
