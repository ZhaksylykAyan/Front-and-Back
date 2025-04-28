<template>
  <div class="chat-modal" ref="modalRef">
    <div class="chat-drag-handle" @mousedown="startDrag">
      <span>Чаты</span>
      <button @click="closeModal" class="close-btn">✕</button>
    </div>

    <div class="chat-content">
      <div class="chat-left">
        <ul class="chat-list">
          <li
            v-for="chat in sortedChats"
            :key="chat.id"
            @click="selectChat(chat.id)"
            :class="{ active: chat.id === chatStore.activeChatId }"
          >
            <div class="chat-item">
              <img
                :src="getOtherParticipant(chat).photo || defaultAvatar"
                class="avatar"
                alt="avatar"
              />
              <div class="chat-info">
                <div class="top-line">
                  <strong class="full-name">{{
                    getOtherParticipant(chat).fullName
                  }}</strong>
                  <small class="last-time">
                    {{
                      chatStore.chatLastMessages[chat.id]?.timestamp
                        ? dayjs(
                            chatStore.chatLastMessages[chat.id].timestamp
                          ).format("HH:mm")
                        : ""
                    }}
                  </small>
                </div>
                <div class="bottom-line">
                  <span class="last-message">
                    {{
                      chatStore.chatLastMessages[chat.id]?.content ||
                      "Нет сообщений"
                    }}
                  </span>

                  <!-- Бейдж непрочитанных рядом с сообщением -->
                  <span
                    v-if="chatStore.unreadCounts[chat.id] > 0"
                    class="unread-badge"
                  >
                    {{
                      chatStore.unreadCounts[chat.id] > 9
                        ? "9+"
                        : chatStore.unreadCounts[chat.id]
                    }}
                  </span>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <div class="chat-right" v-if="chatStore.activeChatId">
        <ChatWindow />
      </div>
      <div class="chat-right empty" v-else>
        <p>Выберите чат, чтобы начать общение</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import { useChatStore } from "../../store/chat";
import ChatWindow from "./ChatWindow.vue";
import axios from "axios";
import { useAuthStore } from "../../store/auth";
import dayjs from "dayjs"; // если ещё не подключил

const chatStore = useChatStore();
const authStore = useAuthStore();
const modalRef = ref(null);
let offset = { x: 0, y: 0 };
let isDragging = false;
const defaultAvatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png";
const closeModal = () => {
  chatStore.closeChatModal();
};

const fetchChats = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/chats/", {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    chatStore.setChatList(res.data);

    for (const chat of res.data) {
      const messagesRes = await axios.get(
        `http://127.0.0.1:8000/api/chats/${chat.id}/messages/`,
        {
          headers: { Authorization: `Bearer ${authStore.token}` },
        }
      );

      const messages = messagesRes.data;
      if (messages.length > 0) {
        const lastMsg = messages[messages.length - 1];
        chatStore.setLastMessage(chat.id, {
          content: lastMsg.content,
          timestamp: lastMsg.timestamp,
        });
      } else {
        chatStore.setLastMessage(chat.id, {
          content: "Нет сообщений",
          timestamp: null,
        });
      }

      const unreadCount = messages.filter(
        (m) => !m.is_read && m.sender.email !== authStore.user.email
      ).length;
      chatStore.unreadCounts[chat.id] = unreadCount;
    }
  } catch (err) {
    console.error("Failed to load chats", err);
  }
};
const sortedChats = computed(() => {
  return [...chatStore.chatList]
    .filter((chat) => chatStore.chatLastMessages[chat.id]) // 🛡️ Фильтруем только те, у кого есть последнее сообщение
    .sort((a, b) => {
      const timeA = new Date(
        chatStore.chatLastMessages[a.id].timestamp
      ).getTime();
      const timeB = new Date(
        chatStore.chatLastMessages[b.id].timestamp
      ).getTime();
      return timeB - timeA;
    });
});

const getLastMessageTime = (chatId) => {
  const messages = chatStore.chatMessagesByChatId[chatId] || [];
  if (messages.length > 0) {
    const lastMsg = messages[messages.length - 1];
    return dayjs(lastMsg.timestamp).format("HH:mm"); // 🕑 форматируем красиво
  }
  return ""; // если нет сообщений
};
const getOtherParticipant = (chat) => {
  const currentId = authStore.user.id;
  const other = chat.participants.find((u) => u.id !== currentId);

  return {
    fullName: other?.profile
      ? `${other.profile.first_name || ""} ${
          other.profile.last_name || ""
        }`.trim()
      : other?.email,
    photo: other?.profile?.photo
      ? `http://127.0.0.1:8000${other.profile.photo}`
      : null,
  };
};
const getLastMessage = (chatId) => {
  const messages = chatStore.chatMessagesByChatId[chatId] || [];
  if (messages.length > 0) {
    return messages[messages.length - 1].content;
  }
  return "";
};

const selectChat = async (id) => {
  if (chatStore.activeChatId !== id) {
    chatStore.setActiveChat(id);
    await chatStore.fetchMessages(id);

    // Сбросить счетчик непрочитанных
    chatStore.resetUnread(id);

    // Отправить на сервер запросы на пометку прочитанными
    const unreadMessages = chatStore.chatMessagesByChatId[id]?.filter(
      (msg) => !msg.is_read && msg.sender.email !== authStore.user.email
    );

    if (unreadMessages && unreadMessages.length > 0) {
      for (const msg of unreadMessages) {
        await axios.patch(
          `http://127.0.0.1:8000/api/messages/${msg.id}/read/`,
          {},
          { headers: { Authorization: `Bearer ${authStore.token}` } }
        );
      }
    }
  }
};

const startDrag = (e) => {
  isDragging = true;
  const modal = modalRef.value;
  offset = {
    x: e.clientX - modal.offsetLeft,
    y: e.clientY - modal.offsetTop,
  };
  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", stopDrag);
};

const onDrag = (e) => {
  if (!isDragging || !modalRef.value) return;
  const modal = modalRef.value;

  const newX = e.clientX - offset.x;
  const newY = e.clientY - offset.y;

  const maxX = window.innerWidth - modal.offsetWidth;
  const maxY = window.innerHeight - modal.offsetHeight;

  const clampedX = Math.min(Math.max(0, newX), maxX);
  const clampedY = Math.min(Math.max(0, newY), maxY);

  modal.style.left = `${clampedX}px`;
  modal.style.top = `${clampedY}px`;
  modal.style.right = "unset";
  modal.style.bottom = "unset";
  modal.style.transform = "none";

  // 💾 сохраняем реальные значения
  localStorage.setItem(
    "chatModalPosition",
    JSON.stringify({ top: clampedY, left: clampedX })
  );
};

const stopDrag = () => {
  isDragging = false;
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopDrag);
};

onMounted(() => {
  chatStore.clearActiveChat();
  fetchChats();

  const modal = modalRef.value;
  if (!modal) return;

  const saved = localStorage.getItem("chatModalPosition");
  if (saved) {
    const { top, left } = JSON.parse(saved);
    modal.style.top = `${top}px`;
    modal.style.left = `${left}px`;
    modal.style.transform = "none";
  } else {
    const centerX = (window.innerWidth - modal.offsetWidth) / 2;
    modal.style.left = `${centerX}px`;
  }
});

onBeforeUnmount(() => stopDrag());
</script>

<style scoped>
.chat-modal {
  position: fixed;
  top: 100px;
  width: 1000px;
  height: 600px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-drag-handle {
  background: #f1f3f5;
  padding: 10px 16px;
  font-weight: bold;
  cursor: grab;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.chat-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.chat-left {
  width: 30%;
  border-right: 1px solid #eee;
  padding: 16px;
  overflow-y: auto;
}
.chat-left-part {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1; /* ⚡ левая часть растягивается */
  overflow: hidden;
}
.chat-list {
  list-style: none;
  padding: 0;
}
.chat-list li {
  padding: 10px;
  cursor: pointer;
  border-radius: 8px;
  transition: 0.2s;
}
.chat-list li:hover {
  background-color: #f5f5f5;
}
.chat-list li.active {
  background-color: #e3efff;
}

.chat-right {
  flex: 1;
  padding: 16px;
  position: relative;
}
.chat-right.empty {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #777;
  font-size: 16px;
}

.close-btn {
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  font-weight: bold;
  color: #333;
}
.unread-badge {
  background-color: red;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 12px;
  margin-left: 6px;
}
.chat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.chat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.last-message {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bottom-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  gap: 8px;
}
.unread-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
}
.last-time {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}
</style>
