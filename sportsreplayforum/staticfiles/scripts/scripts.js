
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
// Get the switches and containerers
const switchCheckbox1 = document.getElementById('flexSwitchCheckDefault');
const videoContainer = document.querySelector('.show-video-container');
const switchCheckbox2 = document.getElementById('flexSwitchCheckDefault2');
const resultsContainer = document.querySelector('.show-score-container');

// Event listener for the first switch
switchCheckbox1.addEventListener('change', () => {
  videoContainer.style.display = switchCheckbox1.checked ? 'block' : 'none';
  if (switchCheckbox1.checked) {
    scrollToElement(videoContainer);
  }
});

// Event listener for the second switch
switchCheckbox2.addEventListener('change', () => {
  resultsContainer.style.display = switchCheckbox2.checked ? 'block' : 'none';
  if (switchCheckbox2.checked) {
    scrollToElement(resultsContainer);
  }
});

// Function to scroll to the element smoothly
function scrollToElement(element) {
  element.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
