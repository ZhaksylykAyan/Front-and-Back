<template>
  <div class="chat-window">
    <div class="chat-header">
      <router-link :to="getOtherUserProfileLink" class="user-info">
        <img :src="otherUserPhoto || defaultAvatar" class="header-avatar" alt="avatar" />
        <div class="name-status">
          <p class="user-name">{{ otherUserFullName }}</p>
          <span :class="{ online: isOnline }">
            {{ userStatusText }}
          </span>
        </div>
      </router-link>
    </div>

    <div class="chat-messages" ref="msgContainer">
      <div
        v-for="(msg, index) in sortedMessages"
        :key="msg.id"
      >
        <div v-if="shouldShowDate(index)" class="date-separator">
          {{ formatDate(msg.timestamp) }}
        </div>

        <div
          :class="[
            'message-container',
            { own: msg.sender.email === authStore.user.email }
          ]"
        >
          <div
            :class="[
              'message-bubble',
              { own: msg.sender.email === authStore.user.email }
            ]"
          >
            <span class="message-text">{{ msg.content }}</span>
            <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
          </div>
        </div>
      </div>

      <div v-if="chatStore.typingUser && chatStore.typingUser !== authStore.user.email" class="typing">
        {{ chatStore.typingUser }} is typing...
      </div>
    </div>

    <form @submit.prevent="sendMessage" class="chat-input">
      <input
        v-model="newMessage"
        @input="sendTyping"
        type="text"
        placeholder="Type a message..."
      />
      <button type="submit">Send</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed, onBeforeUnmount } from "vue";
import { useChatStore } from "../../store/chat";
import { useAuthStore } from "../../store/auth";
import axios from "axios";
import dayjs from "dayjs";

const defaultAvatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png";
const chatStore = useChatStore();
const authStore = useAuthStore();
const msgContainer = ref(null);
const newMessage = ref("");
const ws = ref(null);
const isOnline = ref(false);
const lastSeen = ref(null);
let typingTimeout = null;
const isUserNearBottom = ref(true);
const showScrollButton = ref(false);

const formatTime = (ts) => dayjs(ts).format("HH:mm");

const formatDate = (ts) => {
  const date = dayjs(ts);
  const today = dayjs();
  const yesterday = dayjs().subtract(1, "day");

  if (date.isSame(today, "day")) {
    return "Today";
  } else if (date.isSame(yesterday, "day")) {
    return "Yesterday";
  } else {
    return date.format("D MMMM");
  }
};

const shouldShowDate = (index) => {
  const messages = chatStore.chatMessagesByChatId[chatStore.activeChatId] || [];
  if (index === 0) return true;
  const currentMsgDate = dayjs(messages[index].timestamp).format("YYYY-MM-DD");
  const prevMsgDate = dayjs(messages[index - 1].timestamp).format("YYYY-MM-DD");
  return currentMsgDate !== prevMsgDate;
};

const otherUser = computed(() => {
  const chat = chatStore.chatList.find((c) => c.id === chatStore.activeChatId);
  if (!chat) return null;
  return chat.participants.find((u) => u.id !== authStore.user.id) || null;
});

const otherUserFullName = computed(() => {
  if (!otherUser.value) return "Unknown";
  if (otherUser.value.profile) {
    return `${otherUser.value.profile.first_name || ""} ${otherUser.value.profile.last_name || ""}`.trim();
  }
  return otherUser.value.email;
});

const otherUserPhoto = computed(() => {
  if (!otherUser.value) return null;
  if (otherUser.value.profile?.photo) {
    return `http://127.0.0.1:8000${otherUser.value.profile.photo}`;
  }
  return null;
});

const getOtherUserId = () => {
  const chat = chatStore.chatList.find((c) => c.id === chatStore.activeChatId);
  return chat?.participants?.find((u) => u.id !== authStore.user.id)?.id;
};

const getOtherUserProfileLink = computed(() => {
  if (!otherUser.value) return "#";
  if (otherUser.value.role === "Student") {
    return `/students/${otherUser.value.id}`;
  } else if (otherUser.value.role === "Supervisor") {
    return `/supervisors/${otherUser.value.id}`;
  }
  return "#";
});

const userStatusText = computed(() => {
  if (isOnline.value) {
    return "Online";
  }
  if (!lastSeen.value) {
    return "Offline";
  }
  const now = dayjs();
  const seen = dayjs(lastSeen.value);
  const diffMinutes = now.diff(seen, "minute");
  const diffHours = now.diff(seen, "hour");
  const diffDays = now.diff(seen, "day");

  if (diffMinutes < 1) {
    return "last seen just now";
  }
  if (diffMinutes < 60) {
    return `last seen ${diffMinutes} minute${diffMinutes > 1 ? "s" : ""} ago`;
  }
  if (diffHours < 24) {
    return `last seen ${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  }
  if (diffDays === 1) {
    return `last seen yesterday at ${seen.format("HH:mm")}`;
  }
  return `last seen ${seen.format("D MMMM")} at ${seen.format("HH:mm")}`;
});

const fetchUserStatus = async () => {
  const userId = getOtherUserId();
  if (userId) {
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/users/${userId}/status/`);
      isOnline.value = res.data.is_online;
      lastSeen.value = res.data.last_seen;
    } catch (error) {
      console.error("Failed to fetch user status:", error);
    }
  }
};

const connectWebSocket = () => {
  const token = authStore.token;
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  if (ws.value) {
    ws.value.close();
  }
  ws.value = new WebSocket(`${protocol}://127.0.0.1:8000/ws/chat/${chatStore.activeChatId}/?token=${token}`);

  ws.value.onopen = () => {
    console.log("Chat WebSocket connected");
    pingOnline();
    setInterval(pingOnline, 30000);
  };

  ws.value.onclose = () => {
    console.log("Chat WebSocket closed, reconnecting...");
    setTimeout(connectWebSocket, 3000);
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const chatId = parseInt(data.chat_id);

    if (data.type === "message" && data.message) {
      const message = {
        content: data.message,
        sender: { email: data.sender },
        timestamp: data.timestamp,
        is_read: chatId === chatStore.activeChatId,
      };
      chatStore.addMessage(chatId, message);
      chatStore.setLastMessage(chatId, {
        content: message.content,
        timestamp: message.timestamp,
      });
      if (chatId !== chatStore.activeChatId) {
        chatStore.incrementUnread(chatId);
      } else {
        scrollToBottom();
      }
    }

    if (data.type === "typing") {
      chatStore.setTypingUser(data.user);
      if (typingTimeout) clearTimeout(typingTimeout);
      typingTimeout = setTimeout(() => chatStore.setTypingUser(null), 2000);
    }
  };

  ws.value.onerror = (err) => {
    console.error("WebSocket error:", err);
  };
};

const sendMessage = async () => {
  if (!newMessage.value || !ws.value) return;
  const messageContent = newMessage.value;
  ws.value.send(JSON.stringify({ message: messageContent }));

  try {
    await axios.post(`http://127.0.0.1:8000/api/chats/${chatStore.activeChatId}/messages/`, { content: messageContent }, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    await chatStore.fetchMessages(chatStore.activeChatId);
    chatStore.setLastMessage(chatStore.activeChatId, {
      content: messageContent,
      timestamp: new Date().toISOString(),
    });
  } catch (err) {
    console.error("Failed to save message", err);
  }

  newMessage.value = "";
};

const sortedMessages = computed(() => {
  const messages = chatStore.chatMessagesByChatId[chatStore.activeChatId] || [];
  return [...messages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
});

const sendTyping = () => {
  if (!ws.value) return;
  ws.value.send(JSON.stringify({ type: "typing" }));
};

const pingOnline = () => {
  if (ws.value?.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({ type: "ping" }));
  }
};

const onScroll = () => {
  if (!msgContainer.value) return;
  const { scrollTop, scrollHeight, clientHeight } = msgContainer.value;
  isUserNearBottom.value = scrollTop + clientHeight >= scrollHeight - 100;
  showScrollButton.value = !isUserNearBottom.value;
};

const scrollToBottom = async (force = false) => {
  await nextTick();
  if (msgContainer.value && (isUserNearBottom.value || force)) {
    msgContainer.value.scrollTo({
      top: msgContainer.value.scrollHeight,
      behavior: "smooth",
    });
  }
};

onMounted(async () => {
  if (chatStore.activeChatId) {
    await chatStore.fetchMessages(chatStore.activeChatId);
    await nextTick();
    scrollToBottom();
    connectWebSocket();
    await fetchUserStatus();
  }
  if (msgContainer.value) {
    msgContainer.value.addEventListener("scroll", onScroll);
  }
});

onBeforeUnmount(() => {
  if (msgContainer.value) {
    msgContainer.value.removeEventListener("scroll", onScroll);
  }
});

watch(
  () => chatStore.chatMessagesByChatId[chatStore.activeChatId],
  async () => {
    await nextTick();
    scrollToBottom();
  },
  { deep: true }
);

watch(
  () => chatStore.activeChatId,
  async () => {
    await fetchUserStatus();
  }
);
</script>


<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chat-header {
  padding: 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #ccc;
  display: flex;
  justify-content: space-between;
  font-weight: bold;
}
.chat-header .online {
  color: green;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.message-container {
  display: flex;
  justify-content: flex-start;
}
.message-container.own {
  justify-content: flex-end;
}
.message-bubble {
  background: #f1f1f1;
  padding: 8px 12px;
  border-radius: 18px;
  max-width: 70%;
  min-width: 40px;
  display: inline-flex;
  flex-direction: column;
  position: relative;
  word-break: break-word;
}
.message-bubble.own {
  background: #dcf8c6;
  text-align: right;
}
.message-text {
  font-size: 14px;
  margin-bottom: 4px;
}
.message-time {
  font-size: 10px;
  color: #777;
  align-self: flex-end;
}
.chat-input {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid #ccc;
}
.chat-input input {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
}
.chat-input button {
  padding: 10px 16px;
  border-radius: 8px;
  background: #007bff;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
}
.typing {
  font-style: italic;
  color: #555;
  margin-top: 4px;
}
.date-separator {
  text-align: center;
  margin: 10px 0;
  font-weight: bold;
  color: #666;
  font-size: 13px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
}
.user-info:hover .user-name {
  text-decoration: underline;
}
.header-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}
.name-status {
  display: flex;
  flex-direction: column;
}
.user-name {
  font-weight: bold;
  margin: 0;
}

</style>
