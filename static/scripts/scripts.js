// Convert UTC to local time
document.addEventListener("DOMContentLoaded", function () {
  const eventElements = document.querySelectorAll('.event-datetime');

  eventElements.forEach(function (element) {
    const utcTime = element.getAttribute('data-utc');
    const localDate = new Date(utcTime);

    if (!isNaN(localDate)) {
      const localTimeString = localDate.toLocaleString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false // Use 24-hour format
      });
      element.textContent = localTimeString;
    } else {
      element.textContent = 'Invalid date';
    }
  });
});

// Spoiler Switches
const switchCheckbox1 = document.getElementById('flexSwitchCheckDefault');
const videoContainer = document.querySelector('.show-video-container');

if (switchCheckbox1) {
  switchCheckbox1.addEventListener('change', () => {
    videoContainer.style.display = switchCheckbox1.checked ? 'block' : 'none';
    if (switchCheckbox1.checked) {
      scrollToElement(videoContainer);
    }
  });
  } else {
    console.warn("Element with ID 'flexSwitchCheckDefault' not found.");
}

function scrollToElement(element) {
  element.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Modal Pop up
document.addEventListener("DOMContentLoaded", function() {
  if (!localStorage.getItem('welcomeModalShown')) {
    console.log("Modal code is running!");
    $('#welcomeModal').modal('show');
    localStorage.setItem('welcomeModalShown', 'true');
  }
});

// Event scroller
const eventsList = document.getElementById('events-list');
const container = eventsList.parentElement;


container.addEventListener('scroll', handleScroll);

function handleScroll() {
  if (container.scrollTop + container.offsetHeight >= container.scrollHeight) {
    loadMoreEvents();
  }
}

function loadMoreEvents() {
  fetch('/events/more/', {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => response.json())
  .then(data => {
    appendEvents(data.events);
  });
}

function appendEvents(events) {
  events.forEach(event => {
    const li = document.createElement('li');
    li.innerHTML = `<!-- event HTML here -->`;
    eventsList.appendChild(li);
  });
}