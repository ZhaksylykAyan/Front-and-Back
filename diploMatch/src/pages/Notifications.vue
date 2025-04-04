<template>
  <div class="notifications-page">
    <div class="notif-list">
      <h2>Notifications</h2>
      <div
        v-for="notif in notifications"
        :key="notif.id"
        class="notif-card"
        :class="{ unread: !notif.is_read, read: notif.is_read }"
      >
        <div class="flex-between">
          <div class="message">
            <span v-if="!notif.is_read" class="dot">●</span>
            <p>{{ notif.message }}</p>
          </div>
          <small class="timestamp">{{ formatTime(notif.timestamp) }}</small>
        </div>

        <div class="actions">
          <button @click="deleteNotification(notif.id)" class="btn btn-delete">
            <i class="fa-solid fa-trash" style="margin-right: 6px"></i> Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { useAuthStore } from "../store/auth";
import { useNotificationStore } from "../store/notifications";

const notificationStore = useNotificationStore();
dayjs.extend(relativeTime);

const notifications = ref([]);
const router = useRouter();
const authStore = useAuthStore();

const fetchNotifications = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/notifications/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    notifications.value = res.data;
  } catch (err) {
    console.error("Load notifications failed", err);
  }
};

const formatTime = (timestamp) => {
  return dayjs(timestamp).fromNow();
};

const markAllAsRead = async () => {
  try {
    await axios.patch(
      "http://127.0.0.1:8000/api/notifications/mark-all-as-read/",
      {},
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    notifications.value.forEach((n) => (n.is_read = true));
    notificationStore.reset();
  } catch (err) {
    console.error("Failed to mark all as read", err);
  }
};

onBeforeUnmount(() => {
  markAllAsRead();
});

const deleteNotification = async (id) => {
  try {
    await axios.delete(`http://127.0.0.1:8000/api/notifications/${id}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    notifications.value = notifications.value.filter((n) => n.id !== id);
  } catch (err) {
    console.error("Delete failed", err);
  }
};

onMounted(() => fetchNotifications());
</script>

<style scoped>
.notifications-page {
  padding-top: 50px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
}

.notif-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notif-card {
  background: #f9f9f9;
  padding: 12px 16px;
  border-radius: 12px;
  border-left: 4px solid #007bff;
  transition: background 0.2s ease;
}

.read {
  color: black;
}

.unread {
  background-color: #e9f3ff;
  font-weight: 600;
}

.dot {
  color: red;
  margin-right: 8px;
  font-size: 18px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timestamp {
  font-size: 0.8rem;
  color: #777;
}

.actions {
  margin-top: 8px;
  display: flex;
  gap: 10px;
}

.btn {
  padding: 4px 8px;
  font-size: 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-read {
  background-color: #d4edda;
}

.btn-delete {
  background-color: #f8d7da;
  color: #721c24;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  transition: 0.3s ease;
}

.btn-delete:hover {
  background-color: #f1b0b7;
  color: #a71d2a;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}
</style>
