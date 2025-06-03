<template>
  <div class="about-container">
    <section>
      <h2>About Us</h2>
      <p>
        We are a team of passionate developers, educators, and students who came together to solve a common academic challenge — helping students efficiently find diploma thesis supervisors and form collaborative project teams. Our platform is designed specifically for the needs of universities and students working on final academic projects.
      </p>
    </section>

    <hr />

    <section>
      <h2>Our Mission</h2>
      <p>
        Our mission is to simplify and enhance the diploma thesis process by providing a centralized, user-friendly digital space where students can connect with potential teammates and supervisors. We aim to foster academic collaboration, improve access to mentorship, and encourage transparency and efficiency in project planning.
      </p>
    </section>

    <hr />

    <section>
      <h2>What Do We Offer</h2>
      <ul>
        <li><strong>Team Matching:</strong> Find and join student teams based on skills, research interests, or project goals.</li>
        <li><strong>Supervisor Search:</strong> Browse and connect with available academic supervisors and thesis topics.</li>
        <li><strong>Project Management Tools:</strong> Track your team’s progress, deadlines, and task assignments.</li>
        <li><strong>Communication:</strong> Built-in chat and notification systems to stay connected and informed.</li>
        <li><strong>User Profiles:</strong> Showcase your academic background, skills, and interests.</li>
      </ul>
    </section>

    <hr />

    <section>
      <h2>Contact Us</h2>
      <p>Have questions, suggestions, or need support? We’d love to hear from you!</p>
      <ul class="contact-list">
        <li>📧 Email: <a href="mailto:aminekka603@gmail.com">aminekka603@gmail.com</a></li>
        <li>🌐 Website: <a href="https://front-12ux6.kinsta.app/login" target="_blank">https://front-12ux6.kinsta.app/login</a></li>
        <li>📍 Location: KBTU, Almaty, Kazakhstan</li>
      </ul>
      <p>Let us help you find the right team and guidance to bring your thesis project to life.</p>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

onMounted(() => {
  window.scrollTo({
    top: 0,
    behavior: 'auto' // или 'smooth' — для анимации
  });
});
</script>

<style scoped>
.about-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px 30px 60px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #0d4a7c;
  line-height: 1.8;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

section {
  margin-bottom: 40px;
}

h2 {
  font-size: 30px;
  color: #002d9e;
  margin-bottom: 16px;
  position: relative;
}

h2::after {
  content: "";
  display: block;
  width: 40px;
  height: 4px;
  background-color: #0d4a7c;
  border-radius: 2px;
  margin-top: 8px;
}

p {
  font-size: 16px;
  margin-bottom: 18px;
  color: #333;
}

ul {
  padding-left: 25px;
  margin-bottom: 16px;
}

ul li {
  margin-bottom: 10px;
  font-size: 15.5px;
  color: #222;
  line-height: 1.6;
}

ul li::marker {
  color: #002d9e;
}

.contact-list a {
  color: #0056b3;
  text-decoration: none;
  font-weight: 500;
}

.contact-list a:hover {
  text-decoration: underline;
}

hr {
  border: none;
  border-top: 1px solid #ddd;
  margin: 40px 0;
}

@media (max-width: 768px) {
  .about-container {
    padding: 80px 20px 40px;
    border-radius: 0;
    box-shadow: none;
  }

  h2 {
    font-size: 24px;
  }

  p, ul li {
    font-size: 15px;
  }
}

</style>
