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

// Spoiler Switches
const switchCheckbox1 = document.getElementById('flexSwitchCheckDefault');
const videoContainer = document.querySelector('.show-video-container');
const switchCheckbox2 = document.getElementById('flexSwitchCheckDefault2');
const resultsContainer = document.querySelector('.show-score-container');

switchCheckbox1.addEventListener('change', () => {
  videoContainer.style.display = switchCheckbox1.checked ? 'block' : 'none';
  if (switchCheckbox1.checked) {
    scrollToElement(videoContainer);
  }
});

switchCheckbox2.addEventListener('change', () => {
  resultsContainer.style.display = switchCheckbox2.checked ? 'block' : 'none';
  if (switchCheckbox2.checked) {
    scrollToElement(resultsContainer);
  }
});

function scrollToElement(element) {
  element.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Modal Pop up
document.addEventListener("DOMContentLoaded", function() {
  if (!localStorage.getItem("welcomeShown")) {
      $('#welcomeModal').modal('show');
      localStorage.setItem("welcomeShown", "true");
  }
});