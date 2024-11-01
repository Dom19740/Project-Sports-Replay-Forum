document.addEventListener("DOMContentLoaded", function() {
    const themeToggle = document.querySelector("#theme-toggle");
    const body = document.body;
  
    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem("theme") || "dark";
    body.classList.add(savedTheme + "-mode");
    themeToggle.innerHTML = savedTheme === "dark" ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
  
    // Toggle theme on button click
    themeToggle.addEventListener("click", function() {
      body.classList.toggle("dark-mode");
      themeToggle.innerHTML = body.classList.contains("dark-mode") ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
      localStorage.setItem("theme", body.classList.contains("dark-mode") ? "dark" : "light");
    });
  });