<template>
  <header class="header">
    <div class="header-left">
      <router-link to="/dashboard" class="logo">
        <span class="brand">diplo<span class="blue">match.</span></span>
      </router-link>
    </div>

    <!-- 🟦 Desktop Navigation -->
    <nav class="nav-menu" v-if="!isMobile">
      <router-link
        v-if="userRole !== 'Supervisor'"
        to="/professors"
        class="nav-item"
      >
        Professors
      </router-link>
      <router-link to="/dashboard" class="nav-item">Projects</router-link>
      <router-link to="/orders" class="nav-item">Requests</router-link>
      <ChatIcon />
      <router-link to="/liked" class="icon">
        <i class="fa-regular fa-heart"></i>
      </router-link>
      <NotificationBell />
      <div class="profile-menu" ref="profileMenu">
        <button class="profile-button" @click="toggleDropdown">
          <i class="fas fa-user"></i>
          <span>{{ authStore.fullProfile?.first_name || "Profile" }}</span>
        </button>
        <div v-if="dropdownOpen" class="dropdown-menu">
          <button @click="goToProfile">View Profile</button>
          <button @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <!-- 📱 Mobile Burger -->
    <div class="burger" v-if="isMobile" @click="burgerOpen = !burgerOpen">
      <i class="fas fa-bars"></i>
    </div>

    <!-- 📱 Mobile Dropdown -->
    <div class="mobile-menu" v-if="burgerOpen">
      <router-link
        v-if="userRole !== 'Supervisor'"
        to="/professors"
        @click="closeMenu"
      >
        Professors
      </router-link>
      <router-link to="/profile" @click="closeMenu">Profile</router-link>
      <router-link to="/dashboard" @click="closeMenu">Projects</router-link>
      <router-link to="/orders" @click="closeMenu">Requests</router-link>
      <router-link to="/liked" @click="closeMenu">Favorites ❤️</router-link>
      <button @click="logout">Logout</button>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import ChatIcon  from "../components/Chat/ChatIcon.vue";
import NotificationBell from "../components/notification/NotificationBell.vue";
const router = useRouter();
const authStore = useAuthStore();
const userRole = authStore.user?.role;
const dropdownOpen = ref(false);
const profileMenu = ref(null);
const burgerOpen = ref(false);
const isMobile = ref(window.innerWidth < 768);

const toggleDropdown = () => (dropdownOpen.value = !dropdownOpen.value);
const goToProfile = () => {
  dropdownOpen.value = false;
  router.push("/profile");
};
const logout = () => {
  authStore.logout();
  dropdownOpen.value = false;
  router.push("/login");
};

const handleClickOutside = (e) => {
  if (profileMenu.value && !profileMenu.value.contains(e.target)) {
    dropdownOpen.value = false;
  }
};

const updateWindowSize = () => {
  isMobile.value = window.innerWidth < 768;
  if (!isMobile.value) burgerOpen.value = false;
  console.log("isMobile:", isMobile.value);
};

const closeMenu = () => (burgerOpen.value = false);

onMounted(() => {
  updateWindowSize();
  window.addEventListener("resize", updateWindowSize);
  document.addEventListener("click", handleClickOutside);
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", updateWindowSize);
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style>
.header {
  position: fixed;
  background: #f8f9fa;
  width: 100%;
  z-index: 1000;
  padding: 15px 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  box-sizing: border-box;
  align-items: center;
}
/* Logo */
.logo {
  text-decoration: none;
  font-family: "Sora", sans-serif;
  color: black;
  font-size: 22px;
  font-weight: bold;
}
.blue {
  color: #002d9e;
}

/* Desktop Menu */
.nav-menu {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
  max-width: 100%;
}
.nav-item {
  font-weight: bold;
  color: black;
  text-decoration: none;
}
.nav-item:hover {
  color: #007bff;
}
.icon {
  font-size: 18px;
  color: black;
  cursor: pointer;
}

/* Profile */
.nav-menu {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
  max-width: 100%;
}

.profile-menu {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.profile-button {
  background: none;
  border: none;
  font-size: 16px;
  display: flex;
  align-items: center;
  font-weight: bold;
  cursor: pointer;
  gap: 5px;
  transition: color 0.3s;
}
.profile-button:hover {
  color: #007bff;
}
.dropdown-menu {
  position: absolute;
  top: 40px;
  background: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.dropdown-menu button {
  padding: 10px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
}
.dropdown-menu button:hover {
  background: #f0f0f0;
}

/* Burger Icon */
.burger {
  display: none;
  font-size: 20px;
  cursor: pointer;
  color: #000;
}

/* Mobile Menu */
.mobile-menu {
  position: fixed; /* was: absolute */
  top: 70px; /* чуть ниже header */
  right: 10px;
  left: 10px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 2000; /* на всякий случай выше header */
}
::v-deep(.mobile-menu) a,
::v-deep(.mobile-menu) button {
  font-weight: bold;
  color: black;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
}

.mobile-menu a,
.mobile-menu button {
  text-align: left;
  font-weight: bold;
  color: black;
  text-decoration: none;
  background: none;
  border: none;
  font-size: 16px;
  padding: 5px 0;
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  .burger {
    display: block;
  }
}
</style>
