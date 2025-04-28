import { defineStore } from "pinia";
import { useAuthStore } from "./auth"; 
import axios from "axios";

export const useChatStore = defineStore("chat", {
  state: () => ({
    isModalOpen: false,
    activeChatId: null,
    chatList: [],
    chatMessagesByChatId: {},  // << Добавили сюда
    typingUser: null,
    unreadCounts: {}, // { chatId: number }
    chatLastMessages: {},
  }),
  actions: {
    toggleModal() { this.isModalOpen = !this.isModalOpen; },
    openChatModal() { this.isModalOpen = true; },
    closeChatModal() { this.isModalOpen = false; },
    clearActiveChat() { this.activeChatId = null; },
    setActiveChat(id: number) { this.activeChatId = id; },
    setChatList(chats: any[]) { this.chatList = chats; },
    setLastMessage(chatId, message) {
      this.chatLastMessages[chatId] = {
        content: message.content,
        timestamp: message.timestamp,
      };
    },
    setMessages(chatId, msgs: any[]) {
      this.chatMessagesByChatId[chatId] = msgs;
    },

    addMessage(chatId, msg: any) {
      if (!this.chatMessagesByChatId[chatId]) {
        this.chatMessagesByChatId[chatId] = [];
      }
      this.chatMessagesByChatId[chatId].push(msg);
    },

    setTypingUser(user: string | null) { this.typingUser = user; },

    incrementUnread(chatId) {
      if (!this.unreadCounts[chatId]) {
        this.unreadCounts[chatId] = 1;
      } else {
        this.unreadCounts[chatId]++;
      }
    },

    resetUnread(chatId) {
      this.unreadCounts[chatId] = 0;
    },

    async fetchMessages(chatId) {
      try {
        const authStore = useAuthStore();
        const res = await axios.get(`http://127.0.0.1:8000/api/chats/${chatId}/messages/`, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        });
        this.setMessages(chatId, res.data);
      } catch (err) {
        console.error("Failed to fetch messages", err);
      }
    },
  },
});
