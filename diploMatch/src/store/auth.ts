import { defineStore } from "pinia";
import axios from "axios";
import { useRouter } from "vue-router";

const API_URL = "http://127.0.0.1:8000/api/users/";
const PROFILE_URL = "http://127.0.0.1:8000/api/profiles/complete-profile/";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("token") || null,
    userHasTeam: false,
    userHasPendingRequest: false,
    fullProfile: null,
    isLoggingIn: false,
  }),

  actions: {
    async register(
      email: string,
      password: string,
      confirmPassword: string,
      role: string
    ) {
      try {
        const response = await axios.post(`${API_URL}register/`, {
          email,
          password,
          confirm_password: confirmPassword,
          role,
        });

        // Store token if backend returns it
        if (response.data.token) {
          this.token = response.data.token;
          localStorage.setItem("token", this.token);
          await this.fetchUser();
        }

        return true;
      } catch (error: any) {
        throw new Error(error.response?.data?.detail || "Registration failed");
      }
    },
    async fetchUser() {
      if (!this.token) {
        console.warn("No token found");
        return;
      }

      try {
        const response = await axios.get(`${API_URL}me/`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.user = response.data;

        // Optionally handle redirect to profile if not complete
        const router = useRouter();
        if (!this.user.is_profile_completed) {
          router.push("/profile");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        this.logout();
      }
    },
    async login(email: string, password: string) {
      this.isLoggingIn = true;
      try {
        const response = await axios.post(`${API_URL}login/`, { email, password });
    
        if (!response.data.access) throw new Error("Access token missing");
    
        this.token = response.data.access;
        localStorage.setItem("token", this.token);
    
        const userResponse = await axios.get(`${API_URL}me/`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
    
        this.user = userResponse.data;
        await this.fetchFullProfile();
    
        return { success: true };
      } catch (error: any) {
        this.token = null;
        localStorage.removeItem("token");
    
        // Добавляем обработку блокировки
        const responseData = error?.response?.data || {};
        const message = responseData?.detail || "Login failed";
    
        throw {
          success: false,
          message,
          blocked: responseData?.blocked || false,
          blockedUntil: responseData?.blocked_until || null,
        };
      } finally {
        this.isLoggingIn = false;
      }
    },    
    
    
    async fetchTeamStatus() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/teams/my/", {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        // ✅ Проверка для случая: объект с id
        if (res.data && typeof res.data === "object" && "id" in res.data) {
          this.userHasTeam = true;
        } else if (Array.isArray(res.data) && res.data.length > 0) {
          // если массив команд — тоже true
          this.userHasTeam = true;
        } else {
          this.userHasTeam = false;
        }
      } catch (err) {
        console.error("❌ Failed to fetch team:", err);
        this.userHasTeam = false;
      }
    },

    async fetchPendingRequest() {
      try {
        const res = await axios.get(
          "http://127.0.0.1:8000/api/teams/my-join-request/",
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );
        this.userHasPendingRequest = res.data.status === "pending";
      } catch {
        this.userHasPendingRequest = false;
      }
    },

    async refreshTeamAndRequestStatus() {
      await this.fetchTeamStatus();
      await this.fetchPendingRequest();
    },

    async updateProfile(profileData: any) {
      try {
        const response = await axios.put(PROFILE_URL, profileData, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.user.is_profile_completed = true;
        localStorage.setItem("user", JSON.stringify(this.user));

        const router = useRouter();
        router.push("/dashboard");

        return response.data;
      } catch (error) {
        throw new Error("Failed to update profile");
      }
    },
    async fetchFullProfile() {
      try {
        const res = await axios.get(PROFILE_URL, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.fullProfile = res.data;
      } catch (error) {
        console.error("Failed to fetch full profile:", error);
      }
    },
    async restoreUser() {
      const token = localStorage.getItem("token");
    
      if (!token || this.user) return; // 🛡 уже восстановлен
    
      this.token = token;
    
      try {
        const response = await axios.get(`${API_URL}me/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.user = response.data;
        await this.fetchFullProfile();
      } catch (error) {
        console.error("Session expired. Logging out.");
        this.logout();
      }
    },

    async logout() {
      try {
        // отправляем logout-запрос на бэкенд
        await axios.post(
          `${API_URL}logout/`,
          {},
          {
            headers: {
              Authorization: `Bearer ${this.token}`,
            },
          }
        );
      } catch (error) {
        console.warn("Logout on server failed or already logged out:", error);
      }
    
      // локальная очистка токена
      this.user = null;
      this.token = null;
      localStorage.removeItem("token");
    
      // редирект по желанию
      const router = useRouter();
      router.push("/login");
    },
    

    async requestPasswordReset(email: string) {
      try {
        await axios.post(`${API_URL}forgot-password/`, { email });
        return { success: true, message: "Reset link sent to your email." };
      } catch (error: any) {
        return {
          success: false,
          message: error.response?.data?.error || "Reset failed.",
        };
      }
    },

    async resetPassword(
      uid: string,
      token: string,
      newPassword: string,
      confirmPassword: string
    ) {
      try {
        await axios.put(`${API_URL}reset-password/${uid}/${token}/`, {
          new_password: newPassword,
          confirm_password: confirmPassword,
        });
        return { success: true, message: "Password reset successful." };
      } catch (error: any) {
        return {
          success: false,
          message: error.response?.data?.error || "Reset failed.",
        };
      }
    },
  },
});