"use strict";

/**
 * app.js — Client-side logic for VoteWise.
 * Handles DOM manipulation, routing (tab switching), and API requests.
 */

const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Generic API caller with basic sessionStorage caching
 * @param {string} endpoint - API endpoint
 * @param {Object} [options] - fetch options
 * @returns {Promise<any>} Response json data
 */
async function cachedApiCall(endpoint, options = {}) {
  const isGET = !options.method || options.method === 'GET';
  
  if (isGET) {
    const cacheKey = `votewise_cache_v2_${endpoint}`;
    const cachedItem = sessionStorage.getItem(cacheKey);
    
    if (cachedItem) {
      try {
        const parsed = JSON.parse(cachedItem);
        if (Date.now() - parsed.timestamp < CACHE_TTL_MS) {
          return parsed.data;
        }
      } catch (e) {
        // Ignored; fetch fresh
      }
    }
  }

  const response = await fetch(endpoint, options);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (isGET) {
    sessionStorage.setItem(`votewise_cache_v2_${endpoint}`, JSON.stringify({
      timestamp: Date.now(),
      data: data
    }));
  }
  
  return data;
}

/**
 * Initialize app including service worker
 */
function init() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(err => {
        console.error('SW Registration Failed:', err);
      });
    });
  }

  // Setup Tabs
  const navTabs = document.querySelectorAll('.nav-tab');
  navTabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.id));
  });

  // Setup Toolkit Eligibility
  document.getElementById('eligibility-form').addEventListener('submit', handleEligibilitySubmission);
  
  // Setup Knowledge base / Ask
  document.getElementById('chat-form').addEventListener('submit', handleChatSubmission);
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const query = chip.getAttribute('data-query');
      document.getElementById('chat-input').value = query;
      handleChatSubmission(new Event('submit'));
    });
  });

  // Setup Info Tab
  document.getElementById('state-selector').addEventListener('change', handleStateSelection);
  
  // Setup Feedback Chips
  document.querySelectorAll('#feedback-chips .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const feedback = chip.getAttribute('data-feedback');
      if (typeof gtag === 'function') {
        gtag('event', 'app_feedback', { 'feedback_type': feedback });
      }
      submitRating(5, feedback); // Auto 5-star for positive chip feedback
    });
  });

  // Setup Stars
  setupStarRatings();

  // Load Initial Tab
  loadTimelineData(); // Load first tab inherently
  
  // Setup Accessibility Features
  setupAccessibility();
  
  if (document.getElementById('mic-btn')) {
    setupSpeechToText();
  }
}

/**
 * Handle switching between bottom navigation tabs
 * @param {string} clickedId - ID of the clicked nav button
 */
function switchTab(clickedId) {
  // Update nav UI
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.classList.remove('active');
    tab.setAttribute('aria-selected', 'false');
  });
  const activeTab = document.getElementById(clickedId);
  activeTab.classList.add('active');
  activeTab.setAttribute('aria-selected', 'true');

  // Update panels
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.add('hidden');
  });
  const targetPanelId = activeTab.getAttribute('aria-controls');
  const targetPanel = document.getElementById(targetPanelId);
  targetPanel.classList.remove('hidden');

  // GA4 event
  if (typeof gtag === 'function') {
    gtag('event', 'screen_view', { 'app_name': 'VoteWise', 'screen_name': targetPanelId });
  }

  // Lazy load content
  if (targetPanelId === 'tab-toolkit' && document.getElementById('document-checklist').children.length === 0) {
    loadToolkitData();
  }
  if (targetPanelId === 'tab-info' && document.getElementById('faq-container').children.length === 0) {
    loadInfoData();
  }
}

/**
 * Fetch and construct the timeline
 */
async function loadTimelineData() {
  try {
    const timelineData = await cachedApiCall('/api/timeline');
    const container = document.getElementById('timeline-container');
    container.innerHTML = '';
    
    timelineData.forEach(item => {
      const tItem = document.createElement('div');
      // Assign specific classes (completed, current, pending)
      tItem.className = `timeline-item ${item.status}`;
      
      let detailsHtml = '';
      if (item.details && item.details.length) {
        detailsHtml = `<ul class="timeline-details text-body-sm">
          ${item.details.map(d => `<li>${d}</li>`).join('')}
        </ul>`;
      }

      tItem.innerHTML = `
        <div class="timeline-icon"></div>
        <div class="timeline-content">
          <div class="timeline-badge">${item.status}</div>
          <h3 class="text-h3">${item.title}</h3>
          <p class="text-body-sm mt-xs mb-sm">${item.description}</p>
          <div class="text-body-sm"><strong>Timing:</strong> ${item.duration}</div>
          <div class="text-body-sm mb-xs"><strong>Example:</strong> ${item.key_dates_example}</div>
          ${detailsHtml}
        </div>
      `;
      container.appendChild(tItem);
    });
  } catch (error) {
    console.error("Timeline error:", error);
  }
}

/**
 * Fetch and inject capabilities for Toolkit
 */
async function loadToolkitData() {
  try {
    const docs = await cachedApiCall('/api/documents');
    const container = document.getElementById('document-checklist');
    container.innerHTML = '';
    
    docs.forEach(doc => {
      const docItem = document.createElement('div');
      docItem.className = 'card bg-surface-variant p-sm flex items-center justify-between mb-xs';
      docItem.innerHTML = `
        <label class="flex items-center flex-1 cursor-pointer">
          <input type="checkbox" class="doc-checkbox toggle-switch mr-md" aria-label="${doc.name}">
          <span>
            <strong class="block text-body font-bold">${doc.name}</strong>
            <span class="text-body-sm text-secondary">${doc.description}</span>
          </span>
        </label>
      `;
      container.appendChild(docItem);
    });

    // Add event listeners for readiness score
    document.querySelectorAll('.doc-checkbox').forEach(cb => {
      cb.addEventListener('change', calculateReadinessScore);
    });

  } catch (error) {
    console.error("Documents error:", error);
  }
}

/**
 * Handle form submission for eligibility
 * @param {Event} e Form submission event
 */
async function handleEligibilitySubmission(e) {
  e.preventDefault();
  
  const age = parseInt(document.getElementById('voter-age').value, 10);
  const is_citizen = document.getElementById('voter-citizen').checked;
  const is_resident = document.getElementById('voter-resident').checked;
  
  try {
    const response = await fetch('/api/eligibility', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ age, is_citizen, is_resident })
    });
    const result = await response.json();
    
    if (typeof gtag === 'function') {
      gtag('event', 'toolkit_check', { 'eligible': result.eligible, 'age': age });
    }

    const resultDiv = document.getElementById('eligibility-result');
    resultDiv.classList.remove('hidden');
    resultDiv.textContent = result.reason;
    if (result.eligible) {
      resultDiv.innerHTML = `<span style="color: var(--success);"><span class="material-symbols-outlined align-middle">check_circle</span> You are eligible to register!</span>`;
      window.isEligible = true;
    } else {
      resultDiv.innerHTML = `<span style="color: var(--error);"><span class="material-symbols-outlined align-middle">cancel</span> ${result.reason}</span>`;
      window.isEligible = false;
    }
    
    calculateReadinessScore();
  } catch (error) {
    console.error("Eligibility API error:", error);
  }
}

/**
 * Handle Chat interaction
 * @param {Event} e Form submission event
 */
async function handleChatSubmission(e) {
  e.preventDefault();
  const inputEl = document.getElementById('chat-input');
  const message = inputEl.value.trim();
  if (!message) return;
  
  inputEl.value = '';
  addChatMessage(message, 'user', false);
  
  // Show typing ...
  const typMsgId = 'typing-' + Date.now();
  const typingIndicator = `
    <div class="typing-indicator" id="${typMsgId}">
      <span></span><span></span><span></span>
    </div>
  `;
  addChatMessage(typingIndicator, 'assistant', false);
  
  try {
    const response = await fetch('/api/concierge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message })
    });
    
    const result = await response.json();
    
    // Parse markdown if available
    const finalHtml = typeof marked !== 'undefined' ? marked.parse(result.reply) : result.reply;
    
    const msgElement = document.getElementById(typMsgId).parentElement;
    msgElement.innerHTML = finalHtml;

    if (typeof gtag === 'function') {
      gtag('event', 'ai_interaction', { 'query_length': message.length });
    }
  } catch (error) {
    const msgElement = document.getElementById(typMsgId).parentElement;
    msgElement.innerHTML = "Sorry, I am having trouble connecting to the network.";
  }
}

/**
 * Helper to append messages to chat
 * @param {string} text - The message text
 * @param {string} type - 'user' | 'assistant'
 * @param {boolean} parseMarkdown - Whether to parse markdown
 * @returns {HTMLElement} The created message node
 */
function addChatMessage(text, type, parseMarkdown = true) {
  const container = document.getElementById('chat-messages');
  const wrapper = document.createElement('div');
  wrapper.className = `message-wrapper ${type}`;
  
  const icon = type === 'user' ? 'person' : 'smart_toy';
  
  let contentHtml = text;
  if(parseMarkdown && typeof marked !== 'undefined' && type === 'assistant') {
    contentHtml = marked.parse(text);
  }

  let actionsHtml = '';
  if (type === 'assistant') {
    actionsHtml = `
      <div class="message-actions">
        <button class="action-btn" onclick="readAloud(this)" aria-label="Read Aloud"><span class="material-symbols-outlined">volume_up</span> Read</button>
        <button class="action-btn" onclick="copyText(this)" aria-label="Copy to clipboard"><span class="material-symbols-outlined">content_copy</span> Copy</button>
      </div>
    `;
  }
  
  wrapper.innerHTML = `
    <div class="avatar"><span class="material-symbols-outlined">${icon}</span></div>
    <div class="message-content">
      <div class="message glass">${contentHtml}</div>
      ${actionsHtml}
    </div>
  `;
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
  
  return wrapper.querySelector('.message');
}

// Read Aloud Function (TTS)
window.readAloud = function(btn) {
  if (!('speechSynthesis' in window)) return;
  const msgDiv = btn.closest('.message-content').querySelector('.message');
  const text = msgDiv.innerText;
  
  const utterance = new SpeechSynthesisUtterance(text);
  const icon = btn.querySelector('.material-symbols-outlined');
  icon.textContent = 'volume_off';
  btn.onclick = () => {
    window.speechSynthesis.cancel();
    icon.textContent = 'volume_up';
    btn.onclick = () => window.readAloud(btn);
  };
  
  utterance.onend = () => {
    icon.textContent = 'volume_up';
    btn.onclick = () => window.readAloud(btn);
  };
  window.speechSynthesis.speak(utterance);
}

// Copy text
window.copyText = function(btn) {
  const msgDiv = btn.closest('.message-content').querySelector('.message');
  const text = msgDiv.innerText;
  navigator.clipboard.writeText(text);
  const icon = btn.querySelector('.material-symbols-outlined');
  icon.textContent = 'check';
  setTimeout(() => icon.textContent = 'content_copy', 2000);
}

// Speech to text setup
function setupSpeechToText() {
  const micBtn = document.getElementById('mic-btn');
  const inputEl = document.getElementById('chat-input');
  
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    micBtn.style.display = 'none';
    return;
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  
  let isRecording = false;
  
  micBtn.addEventListener('click', () => {
    if (isRecording) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });
  
  recognition.onstart = () => {
    isRecording = true;
    micBtn.style.background = 'var(--error)';
    micBtn.querySelector('span').style.color = 'white';
    inputEl.placeholder = 'Listening...';
  };
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    inputEl.value = transcript;
    handleChatSubmission(new Event('submit'));
  };
  
  recognition.onend = () => {
    isRecording = false;
    micBtn.style.background = 'var(--surface-variant)';
    micBtn.querySelector('span').style.color = 'var(--primary)';
    inputEl.placeholder = 'Ask a question...';
  };
}

/**
 * Handles dropdown selection for Info tab
 * @param {Event} e Change event
 */
async function handleStateSelection(e) {
  const value = e.target.value;
  const detailsDiv = document.getElementById('state-details');
  if (!value) {
    detailsDiv.classList.add('hidden');
    return;
  }
  
  try {
    const details = await cachedApiCall(`/api/state/${value}`);
    document.getElementById('state-voters').textContent = details.registered_voters;
    document.getElementById('state-ls').textContent = details.seats_lok_sabha;
    document.getElementById('state-turnout').textContent = details.turnout_percentage;
    document.getElementById('state-upcoming').textContent = details.upcoming_election;
    document.getElementById('state-fun-fact').textContent = details.fun_fact;
    
    if (typeof gtag === 'function') {
      gtag('event', 'state_lookup', { 'state_name': details.name });
    }

    detailsDiv.classList.remove('hidden');
  } catch (err) {
    console.error("State API Error", err);
    detailsDiv.classList.add('hidden');
  }
}

/**
 * Fetch and populate FAQ and Rights Data
 */
async function loadInfoData() {
  try {
    const data = await cachedApiCall('/api/faq');
    const rightsContainer = document.getElementById('rights-container');
    const faqContainer = document.getElementById('faq-container');
    
    rightsContainer.innerHTML = '';
    faqContainer.innerHTML = '';
    
    // Populate Rights
    const icons = ['schedule', 'accessible', 'visibility_off', 'block', 'report', 'lock'];
    data.rights.forEach((right, idx) => {
      const card = document.createElement('div');
      card.className = 'right-card';
      const icon = icons[idx % icons.length];
      card.innerHTML = `
        <span class="material-symbols-outlined">${icon}</span>
        <h4 class="text-body font-bold mb-xs">${right.title}</h4>
        <p class="text-body-xs" style="opacity: 0.9;">${right.desc}</p>
      `;
      rightsContainer.appendChild(card);
    });
    
    // Populate FAQ
    data.faqs.forEach((faq, idx) => {
      const item = document.createElement('div');
      item.className = 'faq-item';
      item.innerHTML = `
        <button class="faq-header" aria-expanded="false" aria-controls="faq-content-${idx}">
          <span>${faq.q}</span>
          <span class="material-symbols-outlined">expand_more</span>
        </button>
        <div class="faq-content" id="faq-content-${idx}">
          <p class="text-body-sm mt-sm">${faq.a}</p>
        </div>
      `;
      
      const btn = item.querySelector('.faq-header');
      btn.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        // Close all
        document.querySelectorAll('.faq-item').forEach(f => {
          f.classList.remove('active');
          f.querySelector('.faq-header').setAttribute('aria-expanded', 'false');
        });
        
        if (!isActive) {
          item.classList.add('active');
          btn.setAttribute('aria-expanded', 'true');
        }
      });
      
      faqContainer.appendChild(item);
    });
    
  } catch (error) {
    console.error("Info Data Error:", error);
  }
}

/**
 * Sets up star rating interactivity
 */
function setupStarRatings() {
  const stars = document.querySelectorAll('.star');
  
  stars.forEach((star, index) => {
    star.addEventListener('click', () => {
      // Re-set selection
      stars.forEach((s, idx) => {
        if (idx <= index) {
          s.classList.add('selected');
          s.setAttribute('aria-checked', 'true');
        } else {
          s.classList.remove('selected');
          s.setAttribute('aria-checked', 'false');
        }
      });
      submitRating(index + 1);
    });
    
    // Keyboard support
    star.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        star.click();
      }
    });
  });
}

/**
 * Submits feedback
 * @param {number} rating - Value 1-5
 * @param {string} [comment] - Optional comment or chip text
 */
async function submitRating(rating, comment = "") {
  try {
    await fetch('/api/save-feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating: rating, comment: comment })
    });
    document.getElementById('rating-response').classList.remove('hidden');
    setTimeout(() => {
      document.getElementById('rating-response').classList.add('hidden');
    }, 5000);
  } catch (e) {
    console.error("Rating err:", e);
  }
}

// Bootstrap
document.addEventListener('DOMContentLoaded', init);

/**
 * Setup Accessibility Panel & Preferences
 */
function setupAccessibility() {
  const toggleBtn = document.getElementById('a11y-toggle');
  const closeBtn = document.getElementById('a11y-close');
  const panel = document.getElementById('a11y-panel');
  const overlay = document.getElementById('a11y-overlay');
  
  // Toggles
  const toggles = {
    'contrast': { el: document.getElementById('toggle-contrast'), class: 'high-contrast' },
    'text': { el: document.getElementById('toggle-text'), class: 'large-text' },
    'motion': { el: document.getElementById('toggle-motion'), class: 'reduce-motion' },
    'dyslexia': { el: document.getElementById('toggle-dyslexia'), class: 'dyslexia-font' }
  };

  // Open/Close logic
  function openPanel() {
    panel.classList.remove('hidden');
    overlay.classList.remove('hidden');
    toggleBtn.setAttribute('aria-expanded', 'true');
    closeBtn.focus();
  }

  function closePanel() {
    panel.classList.add('hidden');
    overlay.classList.add('hidden');
    toggleBtn.setAttribute('aria-expanded', 'false');
    toggleBtn.focus();
  }

  toggleBtn.addEventListener('click', openPanel);
  closeBtn.addEventListener('click', closePanel);
  overlay.addEventListener('click', closePanel);

  // Keyboard trap for modal (Escape to close)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !panel.classList.contains('hidden')) {
      closePanel();
    }
  });

  // Apply & Save preference
  function applyPreference(key, isEnabled) {
    const className = toggles[key].class;
    if (isEnabled) {
      document.body.classList.add(className);
    } else {
      document.body.classList.remove(className);
    }
    localStorage.setItem(`a11y_${key}`, isEnabled);
  }

  // Load preferences on init
  Object.keys(toggles).forEach(key => {
    const isEnabled = localStorage.getItem(`a11y_${key}`) === 'true';
    toggles[key].el.checked = isEnabled;
    applyPreference(key, isEnabled);

    // Listen for changes
    toggles[key].el.addEventListener('change', (e) => {
      applyPreference(key, e.target.checked);
    });
  });
}

/**
 * Calculate and animate the Voter Readiness Score
 */
function calculateReadinessScore() {
  let score = 0;
  
  if (window.isEligible) {
    score += 40;
  }
  
  const checkboxes = document.querySelectorAll('.doc-checkbox');
  const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
  
  // 1 document is enough for voting, but we scale it slightly for gamification (max 60)
  if (checkedCount > 0) {
    score += Math.min(60, 20 + (checkedCount - 1) * 20); 
  }
  
  // Update UI
  const scoreText = document.getElementById('readiness-score');
  const scoreFill = document.getElementById('gauge-fill');
  const statusText = document.getElementById('readiness-status');
  
  if(!scoreText || !scoreFill) return;

  scoreText.textContent = `${score}%`;
  
  // SVG dash array is 125.6 for the semi-circle
  const offset = 125.6 - (score / 100) * 125.6;
  scoreFill.style.strokeDashoffset = offset;
  
  if (score === 100) {
    statusText.textContent = "You're 100% ready for polling day!";
    scoreText.style.color = "var(--success)";
  } else if (score >= 40) {
    statusText.textContent = "You're eligible! Now gather your documents.";
    scoreText.style.color = "inherit";
  } else {
    statusText.textContent = "Complete the checklist to get ready.";
    scoreText.style.color = "inherit";
  }
}
