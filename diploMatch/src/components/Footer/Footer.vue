<template>
  <footer class="footer">
    <div class="footer-left">
      <img src="../../assets/logo.png" alt="Diplomatch Logo" class="logo" />
      <p class="tagline">Match. Collaborate. Graduate.</p>
      <small>All rights reserved.</small>
    </div>

    <div class="footer-center">
      <ul>
        <li><router-link to="/dashboard">Projects</router-link></li>
        <li><router-link to="/professors">Professors</router-link></li>
        <li><router-link to="/orders">Requests</router-link></li>
        <li><router-link to="/about">About Us</router-link></li>
      </ul>
    </div>

    <div class="footer-right">
      <p>We are on social media:</p>
      <div class="icons">
        <i class="fa-brands fa-instagram"></i>
        <i class="fa-brands fa-telegram"></i>
        <i class="fa-solid fa-envelope"></i>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Ничего не нужно тут, пока всё статичное
</script>

<style scoped>
.footer {
  background-color: #0d4a7c;
  color: white;
  display: flex;
  justify-content: space-between;
  padding: 40px 60px;
  flex-wrap: wrap;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 250px;
}

.logo {
  width: 140px;
  height: auto;
  filter: brightness(0) invert(1);
}

.tagline {
  font-weight: 600;
  margin-top: 8px;
}

.footer-center ul {
  list-style: none;
  padding: 0;
}

.footer-center li {
  margin: 8px 0;
}

.footer-center a {
  color: white;
  text-decoration: none;
  transition: 0.3s ease;
}

.footer-center a:hover {
  text-decoration: underline;
}

.footer-right {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.icons {
  display: flex;
  gap: 16px;
  font-size: 20px;
}

@media (max-width: 768px) {
  .footer {
    flex-direction: column;
    gap: 30px;
    text-align: center;
    align-items: center;
  }

  .footer-center ul {
    padding: 0;
  }
}
.icons i {
  font-size: 20px;
  margin-right: 15px;
  cursor: pointer;
  transition: transform 0.3s;
}

.icons i:hover {
  transform: scale(1.2);
}
</style>
