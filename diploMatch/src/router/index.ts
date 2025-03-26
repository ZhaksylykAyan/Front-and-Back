import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";

// Page Components
import Login from "../pages/Login.vue";
import Register from "../pages/Register.vue";
import Dashboard from "../pages/Dashboard.vue";
import Profile from "../pages/Profile.vue";
import CreateTopic from '../pages/CreateProject.vue';
import PasswordReset from "../pages/PasswordReset.vue";
import Orders from "../pages/Orders.vue";
import StudentProfile from "../components/profiles/students/StudentProfile.vue";
import SupervisorProfile from "../components/profiles/supervisors/SupervisorProfile.vue";
import Professors from "../pages/Professors.vue";
import Notifications from "../pages/Notifications.vue";
import Likes from "../pages/Likes.vue";

const routes = [
  { path: "/dashboard", component: Dashboard, meta: { requiresAuth: true } },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/profile", component: Profile, meta: { requiresAuth: true, requiresProfile: true } },
  { path: "/forgot-password", component: PasswordReset },
  { path: "/reset-password/:uid/:token", component: PasswordReset },
  {
    path: '/create-project',
    name: 'CreateTopic',
    component: CreateTopic,
    meta: { requiresAuth: true },
  },
  {
    path: "/students/:id",
    name: "StudentPublicProfile",
    component: StudentProfile,
    meta: { requiresAuth: true },
    props: route => ({ viewedUserId: route.params.id, readonly: true }),
  },
  {
    path: "/orders",
    name: "Orders",
    component: Orders,
    meta: { requiresAuth: true },
  },
  {
    path: '/professors',
    name: 'Professors',
    component: Professors
  },

  {
    path: '/supervisors/:id',
    name: 'SupervisorProfile',
    component: SupervisorProfile // компонент, который отображает профиль супервизора
  },
  {
    path: "/notifications",
    name: 'Notifications',
    component: Notifications,
  },
  {
    path: "/liked",
    name: 'Liked',
    component: Likes,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const token = localStorage.getItem("token");

  const publicPages = ["/login", "/register", "/forgot-password"];
  const authRequired = to.meta.requiresAuth;

  // If navigating to a public page — allow directly
  if (publicPages.includes(to.path)) {
    return next();
  }

  // No token, trying to access protected page → redirect
  if (authRequired && !token) {
    return next("/login");
  }

  // If token exists but user not loaded → restore user
  if (token && !authStore.user) {
    await authStore.restoreUser();
  }

  // After restore, check again
  if (authRequired && !authStore.token) {
    return next("/login");
  }

  // // Redirect to profile completion page if profile is not completed
  // if (
  //   authStore.user &&
  //   !authStore.user.is_profile_completed &&
  //   to.path !== "/profile"
  // ) {
  //   return next("/profile");
  // }

  return next(); // Allow navigation
});

export default router;