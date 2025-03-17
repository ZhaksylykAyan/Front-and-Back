<template>
  <div>
    <component :is="currentComponent" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../store/auth';

// Импорт всех компонентов
import StudentProfile from '../components/profiles/students/StudentProfile.vue';
import StudentProfileEdit from '../components/profiles/students/StudentProfileEdit.vue';

import SupervisorProfile from '../components/profiles/supervisors/SupervisorProfile.vue';
import SupervisorProfileEdit from '../components/profiles/supervisors/SupervisorProfileEdit.vue';

import DeanOfficeProfile from '../components/profiles/dean/DeanOfficeProfile.vue';
import DeanOfficeProfileEdit from '../components/profiles/dean/DeanOfficeProfileEdit.vue';

const route = useRoute();
const authStore = useAuthStore();

const role = computed(() => authStore.user?.role || '');
const isEdit = computed(() => route.query.edit === 'true');

const currentComponent = computed(() => {
  if (role.value === 'Student') {
    return isEdit.value ? StudentProfileEdit : StudentProfile;
  } else if (role.value === 'Supervisor') {
    return isEdit.value ? SupervisorProfileEdit : SupervisorProfile;
  } else if (role.value === 'Dean Office') {
    return isEdit.value ? DeanOfficeProfileEdit : DeanOfficeProfile;
  } else {
    return null;
  }
});
</script>