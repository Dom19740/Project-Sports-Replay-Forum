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

// Spoiler Switch — swaps poster for video thumbnail matched to poster height
const switchCheckbox1 = document.getElementById('flexSwitchCheckDefault');
const posterContainer = document.getElementById('poster-container');
const videoContainer  = document.getElementById('video-container');
const videoThumb      = document.getElementById('video-thumbnail');
const posterImg       = posterContainer ? posterContainer.querySelector('img') : null;

if (switchCheckbox1 && posterContainer && videoContainer && videoThumb && posterImg) {
  switchCheckbox1.addEventListener('change', () => {
    if (switchCheckbox1.checked) {
      const h = posterImg.offsetHeight;
      if (h > 0) videoThumb.style.height = h + 'px';
      posterContainer.style.display = 'none';
      videoContainer.style.display  = 'flex';
    } else {
      posterContainer.style.display = 'flex';
      videoContainer.style.display  = 'none';
    }
  });
}


// Blurb Switch
const blurbSwitch = document.getElementById('blurbSwitch');
const blurbContainer = document.querySelector('.ai-blurb-container');

if (blurbSwitch && blurbContainer) {
  blurbSwitch.addEventListener('change', () => {
    blurbContainer.style.visibility = blurbSwitch.checked ? 'visible' : 'hidden';
  });
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

// XP strip progress colour
(function () {
  const fill  = document.querySelector('.xp-strip-fill');
  const level = document.querySelector('.xp-strip-level');
  if (!fill || !level) return;

  const pct = parseFloat(fill.style.width) / 100; // 0–1

  // Star colour stops: ice → ocean → orange → burnt → pink
  const stops = [
    [36,  228, 231],  // --one-star-ice
    [149, 208, 187],  // --two-star-ocean
    [246, 147, 63],   // --three-star-orange
    [243, 116, 132],  // --four-star-burnt
    [238, 53,  185],  // --five-star-pink
  ];

  function lerp(a, b, t) { return a + (b - a) * t; }

  function interpolate(stops, t) {
    const seg = stops.length - 1;
    const scaled = t * seg;
    const i = Math.min(Math.floor(scaled), seg - 1);
    const lt = scaled - i;
    return stops[i].map((c, idx) => Math.round(lerp(c, stops[i + 1][idx], lt)));
  }

  // Full gradient spans the whole track — fill just clips how much is visible.
  // background-size = track width / fill width = 100% / pct of the fill element.
  const gradient = stops.map(([r,g,b]) => `rgb(${r},${g},${b})`).join(', ');
  fill.style.background     = `linear-gradient(90deg, ${gradient})`;
  fill.style.backgroundSize = pct > 0 ? `${(1 / pct) * 100}% 100%` : '100% 100%';
  fill.style.backgroundPosition = 'left center';

  // Level circle: solid colour at the current progress point
  const [r, g, b] = interpolate(stops, pct);
  level.style.background = `rgb(${r},${g},${b})`;
}());

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



