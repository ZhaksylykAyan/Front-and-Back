<template>
    <div class="notif-list">
      <h2>Notifications</h2>
      <div v-for="notif in notifications" :key="notif.id" class="notif-card">
        <p>{{ notif.message }}</p>
        <small>{{ new Date(notif.timestamp).toLocaleString() }}</small>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import axios from "axios";
  import { useAuthStore } from "../store/auth";
  
  const notifications = ref([]);
  const authStore = useAuthStore();
  
  const fetchNotifications = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/notifications/", {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      notifications.value = res.data;
    } catch (err) {
      console.error("Load notifications failed", err);
    }
  };
  
  onMounted(() => fetchNotifications());
  </script>
  
  <style scoped>
  .notif-card {
    background: #f9f9f9;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 16px;
    border-left: 4px solid #007bff;
  }
  .read {
    color: green;
    font-weight: bold;
  }
  .unread {
    color: red;
    font-weight: bold;
  }
  </style>
  