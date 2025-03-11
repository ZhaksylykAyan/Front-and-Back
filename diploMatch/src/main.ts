import { createApp } from "vue";
import App from "./App.vue";
import "@fortawesome/fontawesome-free/css/all.css";
import router from "./router";
import { createPinia } from "pinia";
import "./styles/auth.css"
import "./styles/main.css"; // Global styles

const app = createApp(App);

app.use(router);
app.use(createPinia());
app.mount("#app");

