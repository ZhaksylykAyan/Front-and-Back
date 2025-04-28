<template>
    <div class="icon chat-icon" @click="toggleChat">
      <i class="fa-regular fa-comment-dots"></i>
    </div>
  </template>
  
  <script setup>
  import { useChatStore } from "../../store/chat";
  const chatStore = useChatStore();
  
  const toggleChat = () => {
    chatStore.toggleModal(); // будет переключать open/close модалки
  };
  </script>
  
  <style scoped>
  .chat-icon {
    cursor: pointer;
    font-size: 18px;
    color: black;
  }
  .chat-icon:hover {
    color: #007bff;
  }
  </style>
  