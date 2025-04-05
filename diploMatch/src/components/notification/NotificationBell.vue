<template>
  <div class="notification-icon" style="position: relative">
    <router-link to="/notifications">
      <i class="fas fa-bell"></i>
      <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount }}</span>
    </router-link>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "../../store/auth";
import { useNotificationStore } from "../../store/notifications";
import { useRoute } from "vue-router";
const route = useRoute();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
let socket = null;


const fetchUnread = async () => {
  try {
    const res = await axios.get(
      "http://127.0.0.1:8000/api/notifications/unread/",
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );
    notificationStore.setCount(res.data.unread_count);
  } catch (err) {
    console.error("Failed to fetch unread notifications:", err);
  }
};

// 🔥 WebSocket подключение с JWT авторизацией
const connectWebSocket = () => {
  const token = authStore.token;
  if (!token) return; // Если нет токена — не подключаемся

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(
    `${protocol}://127.0.0.1:8000/ws/notifications/?token=${token}`
  );

  socket.onopen = () => {
    console.log("WebSocket Connected ✅");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.message) {
      unreadCount.value += 1; // 📈 Увеличиваем счетчик при новом уведомлении
    }
  };

  socket.onerror = (err) => {
    console.error("WebSocket error:", err);
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected. Reconnecting...");
    setTimeout(connectWebSocket, 3000); // ⏳ Авто-реконнект
  };
};

// 🔥 Автоматическая загрузка уведомлений при загрузке компонента
onMounted(() => {
  if (authStore.token && authStore.user) {
    fetchUnread();
    connectWebSocket();
  }
});


// Очистка при размонтировании
onUnmounted(() => {
  if (socket) {
    socket.close();
  }
});
const unreadCount = computed(() => notificationStore.unreadCount);
</script>

<style scoped>
.notification-icon {
  position: relative;
  display: inline-block;
}

.notification-icon .fas.fa-bell {
  font-size: 18px; /* такой же как у сердечка */
  color: black;
}

.notif-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  background-color: red;
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 50%;
  font-weight: bold;
  line-height: 1;
  z-index: 2;
}

</style>