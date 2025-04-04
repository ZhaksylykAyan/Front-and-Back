// store/notifications.ts
import { defineStore } from "pinia";

interface NotificationState {
  unreadCount: number;
}

export const useNotificationStore = defineStore('notifications', {
  state: (): NotificationState => ({
    unreadCount: 0,
  }),
  actions: {
    setCount(count: number) {
      this.unreadCount = count;
    },
    increment() {
      this.unreadCount += 1;
    },
    reset() {
      this.unreadCount = 0;
    },
  },
});
