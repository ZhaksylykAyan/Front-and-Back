<template>
  <header class="header">
    <!-- Left Side: Logo -->
    <div class="header-left">
      <router-link to="/dashboard" class="logo">
        <span class="brand">diplo<span class="blue">match.</span></span>
      </router-link>
    </div>

    <!-- Right Side: Navigation -->
    <div class="header-right">
      <nav class="nav-menu">
        <router-link to="/professors" class="nav-item">Professors</router-link>
        <router-link to="/dashboard" class="nav-item">Projects</router-link>
        <router-link to="/orders" class="nav-item">Orders</router-link>
        <router-link to="/liked" class="icon">
          <i class="fas fa-heart"></i>
        </router-link>
        <NotificationBell />
      </nav>

      <!-- Profile Dropdown -->
      <div class="profile-menu" ref="profileMenu">
        <button class="profile-button" @click="toggleDropdown">
          <i class="fas fa-user"></i> Profile
        </button>
        <div v-if="dropdownOpen" class="dropdown-menu">
          <button @click="goToProfile">View Profile</button>
          <button @click="logout">Logout</button>
        </div>
      </div>

      <!-- Language Switcher -->
      <div class="language-switch">
        <button @click="switchLanguage('en')">
          <img src="../icons/flags/en.png" alt="English" class="flag-icon" />
        </button>
        <button @click="switchLanguage('ru')">
          <img src="../icons/flags/ru.jpg" alt="Russian" class="flag-icon" />
        </button>
        <button @click="switchLanguage('kz')">
          <img src="../icons/flags/kz.png" alt="Kazakh" class="flag-icon" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import NotificationBell from "../components/notification/NotificationBell.vue";
const router = useRouter();
const authStore = useAuthStore();
const dropdownOpen = ref(false);
const profileMenu = ref(null);

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const goToProfile = () => {
  dropdownOpen.value = false;
  router.push("/profile");
};

const logout = () => {
  authStore.logout();
  dropdownOpen.value = false;
  router.push("/login");
};

const switchLanguage = (lang) => {
  localStorage.setItem("language", lang);
  location.reload(); // You can use i18n change instead of reload if you implement it
};

const handleClickOutside = (event) => {
  if (profileMenu.value && !profileMenu.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
/* Header Container */
.header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 40px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

/* Left Side: Logo */
.logo {
  text-decoration: none;
  font-size: 24px;
  font-weight: bold;
  color: black;
}

.blue {
  color: #0056b3;
}

/* Right Side */
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* Navigation */
.nav-menu {
  display: flex;
  gap: 20px;
}

.nav-item {
  text-decoration: none;
  font-weight: bold;
  color: black;
  transition: color 0.3s;
}

.nav-item:hover {
  color: #007bff;
}

.icon {
  font-size: 18px;
  color: black;
  cursor: pointer;
  position: relative;
}

.icon:hover {
  color: #007bff;
}

/* Notification Bell Badge */
.notification-icon {
  position: relative;
  display: inline-block;
}

.notif-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  background-color: red;
  color: white;
  font-size: 11px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 50%;
  line-height: 1;
  z-index: 2;
}

/* Profile Menu */
.profile-menu {
  position: relative;
}

.profile-button {
  background: none;
  border: none;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  transition: color 0.3s;
}

.profile-button:hover {
  color: #007bff;
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: 40px;
  right: 0;
  background: white;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-width: 140px;
  z-index: 999;
}

.dropdown-menu button {
  background: none;
  border: none;
  padding: 10px;
  text-align: left;
  cursor: pointer;
  width: 100%;
  transition: background 0.3s;
}

.dropdown-menu button:hover {
  background: #f1f1f1;
}

/* Language Switch */
.language-switch {
  display: flex;
  align-items: center;
  gap: 10px;
}

.language-switch button {
  background: none;
  border: none;
  cursor: pointer;
}

.flag-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}
</style>
