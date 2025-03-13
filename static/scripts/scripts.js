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

// Welcome container hider
document.addEventListener('DOMContentLoaded', () => {
  const arrow = document.getElementById('arrow');
  const welcomeContainer = document.querySelector('.welcome-container');

  if (!arrow || !welcomeContainer) {
    console.error('Arrow or Welcome Container not found in the DOM.');
    return;
  }

  const wasHidden = localStorage.getItem('welcomeContainerHidden') === 'true';

  if (wasHidden) {
    welcomeContainer.style.display = 'none';
    arrow.classList.remove('fa-xmark');
    arrow.classList.add('fa-angle-down');
  } else {
    welcomeContainer.style.display = 'block';
    arrow.classList.remove('fa-angle-down');
    arrow.classList.add('fa-xmark');
  }

  arrow.addEventListener('click', () => {

    const isHidden = welcomeContainer.style.display === 'none' || welcomeContainer.style.display === '';

    if (isHidden) {
      welcomeContainer.style.display = 'block';
      arrow.classList.remove('fa-angle-down');
      arrow.classList.add('fa-xmark');

      localStorage.setItem('welcomeContainerHidden', 'false');

    } else {
      welcomeContainer.style.display = 'none';
      arrow.classList.remove('fa-xmark');
      arrow.classList.add('fa-angle-down');
      localStorage.setItem('welcomeContainerHidden', 'true');
    }
  });
});

// Spoiler Switch
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


// Comments Switch
const switchCheckbox2 = document.getElementById('commentsSwitchCheckDefault');
const commentsContainer = document.querySelector('.show-comments-container');

const pageCommentsKey = 'commentsSwitchState_' + window.location.pathname;
const storedCommentsState = localStorage.getItem(pageCommentsKey);

if (storedCommentsState === 'on') {
  switchCheckbox2.checked = true;
  commentsContainer.style.display = 'block';
}

if (switchCheckbox2) {
  switchCheckbox2.addEventListener('change', () => {
    if (switchCheckbox2.checked) {
      commentsContainer.style.display = 'block';
      localStorage.setItem(pageCommentsKey, 'on');
      scrollToElement(commentsContainer);
    } else {
      commentsContainer.style.display = 'none';
      localStorage.setItem(pageCommentsKey, 'off');
    }
  });
} else {
  console.warn("Element with ID 'commentsSwitchCheckDefault' not found.");
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



