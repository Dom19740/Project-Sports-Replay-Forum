// Dark Light Theme switch
document.addEventListener("DOMContentLoaded", function () {
  const themeToggle = document.querySelector("#theme-toggle");
  const body = document.body;

  // Check for saved theme in localStorage
  const savedTheme = localStorage.getItem("theme") || "dark";
  body.classList.add(savedTheme + "-mode");
  themeToggle.innerHTML = savedTheme === "dark" ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';

  // Toggle theme on button click
  themeToggle.addEventListener("click", function () {
    body.classList.toggle("dark-mode");
    themeToggle.innerHTML = body.classList.contains("dark-mode") ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
    localStorage.setItem("theme", body.classList.contains("dark-mode") ? "dark" : "light");
  });
});

// Convert UTC to local time
document.addEventListener("DOMContentLoaded", function () {
  const eventElements = document.querySelectorAll('.event-datetime');

  eventElements.forEach(function (element) {
    const utcTime = element.getAttribute('data-utc');
    // Convert the UTC time string (ISO 8601) to a Date object
    const localDate = new Date(utcTime);

    // Check if the date is valid
    if (!isNaN(localDate)) {
      // Format the date and time for the local time zone
      const localTimeString = localDate.toLocaleString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false // Use 24-hour format
      });
      // Update the span content with the local time string
      element.textContent = localTimeString;
    } else {
      element.textContent = 'Invalid date';
    }
  });
});