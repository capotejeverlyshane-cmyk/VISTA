import { state } from './state.js';
import { API_URL } from './config.js';
import { timeNow, escapeHTML, showToast } from './utils.js';
import { showView, setActiveNav, closeFeedbackModal, closeAllDotsMenus } from './ui.js';
import { saveHistory } from './history.js';
import { speakText } from './voice.js';

const MAX_QUESTION_LENGTH = 500;

/* ==================== QUICK ACTIONS */
export function updateQuickActionsVisibility() {
  const quickActions = document.getElementById("quickActions");
  if (quickActions) quickActions.style.display = state.hasConversation ? "none" : "flex";
  const hero = document.getElementById("welcomeHero");
  if (hero) hero.style.display = state.hasConversation ? "none" : "block";
}

/* ==================== CHAT CORE */
export function clearChat() {
  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return;
  state.autoScrollPaused = false;
  document.getElementById("scrollToBottomBtn")?.classList.remove("visible");
  chatBox.innerHTML = `
    <div class="welcome-hero" id="welcomeHero">
      <h2 class="welcome-title" id="welcomeTitle">${state.loggedIn && state.username ? `How can I help you today, ${state.username}?` : "How can I help you today?"}</h2>
      <p class="welcome-subtitle">Your AI-powered LGU Citizen Assistant</p>
      <div class="welcome-features">
        <div class="welcome-chip"><span>🌐</span> Trilingual Support</div>
        <div class="welcome-chip"><span>⚡</span> Instant Answers</div>
        <div class="welcome-chip"><span>🏛️</span> Government Services</div>
      </div>
      <p class="welcome-hint">Ask me anything about permits, certificates, taxes, schedules, and more.</p>
    </div>
  `;
  state.hasConversation = false;
  updateQuickActionsVisibility();
}

export function startNewChat() {
  state.currentSessionId = Date.now().toString();
  state.currentMessages = [];
  state.context = null;
  state.contextLanguage = null;
  sessionStorage.setItem("vista_current_session", state.currentSessionId);
  sessionStorage.setItem("vista_current_messages", "[]");
  clearChat();
}

export function renderCurrentChat() {
  clearChat();
  if (!state.currentMessages || state.currentMessages.length === 0) return;
  
  let lastUserText = "";
  state.currentMessages.forEach(msg => {
    if (msg.role === "user") lastUserText = msg.text;
    
    const wrapper = addMessage(msg.text, msg.role, true);
    if (msg.role === "bot") {
      const payload = {
        question: lastUserText,
        answer: msg.text,
        intent: "",
        language: state.language
      };
      addMessageActionButtons(wrapper, msg.text, payload);
    }
  });
  
  state.hasConversation = true;
  updateQuickActionsVisibility();
  scrollChat();
}

export function addMessage(text, sender) {
  text = text || "";
  const chatBox = document.getElementById("chat-box");
  const wrapper = document.createElement("div");
  wrapper.className = `message ${sender}`;

  if (sender === "bot") {
    const parsedHTML = typeof marked !== 'undefined' ? marked.parse(text) : escapeHTML(text);
    wrapper.innerHTML = `
      <div class="avatar-dot">V</div>
      <div class="msg-content">
        <div class="bubble markdown-body">${parsedHTML}</div>
        <div class="meta">AI Assistant • ${timeNow()}</div>
      </div>
    `;
  } else {
    wrapper.innerHTML = `
      <div class="msg-content">
        <div class="bubble">${escapeHTML(text)}</div>
        <div class="meta">You • ${timeNow()}</div>
      </div>
    `;
  }

  chatBox.appendChild(wrapper);
  scrollChat();

  if (sender === "user") {
    state.hasConversation = true;
    updateQuickActionsVisibility();
  }

  return wrapper;
}

export function addTypingIndicator() {
  const chatBox = document.getElementById("chat-box");
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";
  wrapper.id = "typingIndicator";
  wrapper.innerHTML = `
    <div class="avatar-dot">V</div>
    <div class="msg-content">
      <div class="bubble typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  chatBox.appendChild(wrapper);
  scrollChat();
}

export function removeTypingIndicator() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

export function typeMessage(messageElement, text, speed = 10) {
  return new Promise((resolve) => {
    const bubble = messageElement.querySelector(".bubble");
    if (!bubble) return resolve();

    bubble.textContent = "";
    let i = 0;
    
    state.typingInterval = setInterval(() => {
      if (state.stopTypingFlag) {
        clearInterval(state.typingInterval);
        state.typingInterval = null;
        if (typeof marked !== 'undefined') {
          bubble.innerHTML = marked.parse(text.substring(0, i));
          bubble.classList.add('markdown-body');
        }
        resolve();
        return;
      }

      i++;
      if (typeof marked !== 'undefined') {
        bubble.innerHTML = marked.parse(text.substring(0, i));
        bubble.classList.add('markdown-body');
      } else {
        bubble.textContent = text.substring(0, i);
      }
      
      scrollChat();
      if (i >= text.length) {
        clearInterval(state.typingInterval);
        state.typingInterval = null;
        resolve();
      }
    }, speed);
  });
}

export function toggleSendButton(isGenerating) {
  const btn = document.querySelector('.send-btn');
  if (!btn) return;
  
  if (isGenerating) {
    btn.disabled = false;
    btn.onclick = stopGenerating;
    btn.setAttribute("aria-label", "Stop generating");
    btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
    btn.title = "Stop Generating";
  } else {
    btn.onclick = sendMessage;
    btn.setAttribute("aria-label", "Send message");
    btn.innerHTML = `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>`;
    btn.title = "Send";
    updateQuestionControls();
  }
}

export function scrollChat() {
  const chatBox = document.getElementById("chat-box");
  if (chatBox && !state.autoScrollPaused) {
      setTimeout(() => {
        if (!state.autoScrollPaused) chatBox.scrollTop = chatBox.scrollHeight;
      }, 50);
  }
}

export function bindChatView() {
  const chatBox = document.getElementById("chat-box");
  const scrollButton = document.getElementById("scrollToBottomBtn");
  const input = document.getElementById("user-input");
  let previousScrollTop = chatBox?.scrollTop || 0;

  chatBox?.addEventListener("scroll", () => {
    const scrollingUp = chatBox.scrollTop < previousScrollTop;
    previousScrollTop = chatBox.scrollTop;
    if (!state.isSending || state.autoScrollPaused || !scrollingUp) return;
    const distanceFromBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight;
    if (distanceFromBottom > 32) {
      state.autoScrollPaused = true;
      scrollButton?.classList.add("visible");
    }
  });

  scrollButton?.addEventListener("click", () => {
    state.autoScrollPaused = false;
    scrollButton.classList.remove("visible");
    scrollChat();
  });

  input?.addEventListener("input", updateQuestionControls);
  input?.addEventListener("input", resizeChatInput);
  updateQuestionControls();
  resizeChatInput();
}

function updateQuestionControls() {
  const input = document.getElementById("user-input");
  if (!input) return;

  const characters = Array.from(input.value);
  if (characters.length > MAX_QUESTION_LENGTH) {
    input.value = characters.slice(0, MAX_QUESTION_LENGTH).join("");
  }

  const characterCount = Array.from(input.value).length;
  const counter = document.getElementById("questionCharCount");
  const sendButton = document.querySelector(".send-btn");
  if (counter) {
    counter.textContent = `${characterCount} / ${MAX_QUESTION_LENGTH}`;
    counter.classList.toggle("at-limit", characterCount >= MAX_QUESTION_LENGTH);
  }
  if (sendButton && !state.isSending) {
    sendButton.disabled = characterCount >= MAX_QUESTION_LENGTH;
  }
}

function resizeChatInput() {
  const input = document.getElementById("user-input");
  if (!input) return;
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 144)}px`;
}

export async function sendMessage() {
  const input = document.getElementById("user-input");
  const voiceBtn = document.getElementById("voiceBtn");
  updateQuestionControls();
  const question = input.value.trim();
  const textLength = Array.from(input.value).length;

  if (!question || textLength >= MAX_QUESTION_LENGTH || state.isSending) return;
  const text = question;

  // Hide old related topics to keep the UI clean
  document.querySelectorAll('.message-related-articles').forEach(el => {
    el.style.display = 'none';
  });

  state.isSending = true;
  state.stopTypingFlag = false;
  state.autoScrollPaused = false;
  document.getElementById("scrollToBottomBtn")?.classList.remove("visible");
  const controller = new AbortController();
  state.chatRequestController = controller;
  input.disabled = true;
  if (voiceBtn) voiceBtn.disabled = true;
  toggleSendButton(true);

  showView("chat");
  setActiveNav("chat");

  if (!state.currentSessionId) {
    state.currentSessionId = Date.now().toString();
    sessionStorage.setItem("vista_current_session", state.currentSessionId);
    state.currentMessages = [];
  }

  state.currentMessages.push({ role: "user", text: text });
  sessionStorage.setItem("vista_current_messages", JSON.stringify(state.currentMessages));

  addMessage(text, "user");
  input.value = "";
  resizeChatInput();
  addTypingIndicator();

  try {
    const payload = {
      message: text,
      language: state.language,
      context: state.context,
      context_language: state.contextLanguage
    };

    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    const data = await response.json();
    removeTypingIndicator();

    const botMsg = addMessage("", "bot");
    let displayReply = data.reply || "No response received.";
    if (data.summary && data.summary !== data.reply && (data.reply || "").length >= 1000) {
      // Format 3-sentence LSA summary into clear executive bullet points
      const points = data.summary
        .split(/(?<=[.!?])\s+/)
        .map(s => s.trim().replace(/^[•\-\*]\s*/, ""))
        .filter(s => s.length > 10);

      const bulletList = points.length > 0
        ? points.map(pt => `> • ${pt}`).join("\n>\n")
        : `> • ${data.summary}`;

      displayReply = `> ⚡ **Quick Summary** *(At a Glance)*\n>\n${bulletList}\n\n---\n\n### 📋 Complete Service Details (Panabo City Charter)\n\n${data.reply}`;
    }
    await typeMessage(botMsg, displayReply);
    if (state.stopTypingFlag) return;

    state.lastBotPayload = {
      question: text,
      answer: data.reply || "",
      intent: data.intent || "",
      language: data.language || state.language
    };

    state.context = data.context || null;
    state.contextLanguage = state.context ? (data.language || null) : null;

    state.currentMessages.push({ role: "bot", text: displayReply });
    sessionStorage.setItem("vista_current_messages", JSON.stringify(state.currentMessages));

    // Save history as a full session
    saveHistory();

    const related = data.related_articles || [];
    const sourceArticle = related.find(a => a.url && a.score > 0.01);
    const otherArticles = related.filter(a => a !== sourceArticle);

    addMessageActionButtons(botMsg, data.reply || "", state.lastBotPayload, sourceArticle);
    addRelatedArticlesToMessage(botMsg, otherArticles);

    if (state.voiceReply && data.reply && !state.stopTypingFlag) {
      setTimeout(() => speakText(data.reply), 500);
    }
  } catch (error) {
    removeTypingIndicator();
    if (error.name !== "AbortError") {
      console.error(error);
      const errorText = "Unable to connect to VISTA server. Please make sure the backend is running.";
      const errMsg = addMessage(errorText, "bot");
      addMessageActionButtons(errMsg, errorText);
    }
  } finally {
    state.isSending = false;
    state.chatRequestController = null;
    state.stopTypingFlag = false;
    state.autoScrollPaused = false;
    document.getElementById("scrollToBottomBtn")?.classList.remove("visible");
    input.disabled = false;
    if (voiceBtn) voiceBtn.disabled = false;
    toggleSendButton(false);
    input.focus();
    resizeChatInput();
  }
}

export function handleKey(event) {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    sendMessage();
  }
}

export function stopGenerating() {
  if (!state.isSending) return;
  state.stopTypingFlag = true;
  state.chatRequestController?.abort();
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}

/* ==================== QUICK ASK */
export function quickAsk(question) {
  const input = document.getElementById("user-input");
  input.value = question;
  input.dispatchEvent(new Event("input", { bubbles: true }));
  sendMessage();
}

export function quickAskAndGo(question) {
  showView("chat");
  setActiveNav("chat");
  const input = document.getElementById("user-input");
  input.value = question;
  input.dispatchEvent(new Event("input", { bubbles: true }));
  sendMessage();
}


/* ==================== MESSAGE ACTIONS ==================== */
export function addMessageActionButtons(msgElement, text, payload = null, sourceArticle = null) {
  const content = msgElement.querySelector(".msg-content");
  
  // Clean up any existing action rows
  const existingRow = content.querySelector(".message-actions-row");
  if (existingRow) existingRow.remove();

  const row = document.createElement("div");
  row.className = "message-actions-row";

  // 1. Speak Button
  const speakBtn = document.createElement("button");
  speakBtn.className = "action-icon-btn";
  speakBtn.title = "Listen";
  speakBtn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
  speakBtn.onclick = () => speakText(text);
  row.appendChild(speakBtn);

  // 2. Copy Button
  const copyBtn = document.createElement("button");
  copyBtn.className = "action-icon-btn";
  copyBtn.title = "Copy";
  copyBtn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
  copyBtn.onclick = async () => {
    try {
      await navigator.clipboard.writeText(text);
      showToast("Copied to clipboard.");
    } catch {
      showToast("Copy failed.");
    }
  };
  row.appendChild(copyBtn);

  // If payload is provided, add Feedback buttons
  if (payload) {
    const upBtn = document.createElement("button");
    upBtn.className = "action-icon-btn";
    upBtn.title = "Helpful";
    upBtn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>`;
    
    const downBtn = document.createElement("button");
    downBtn.className = "action-icon-btn";
    downBtn.title = "Not Helpful";
    downBtn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>`;

    upBtn.onclick = () => { submitFeedback(payload, true, null); upBtn.classList.add("active"); downBtn.classList.remove("active"); upBtn.disabled = true; downBtn.disabled = true; };
    downBtn.onclick = () => { submitFeedback(payload, false, null); downBtn.classList.add("active"); upBtn.classList.remove("active"); upBtn.disabled = true; downBtn.disabled = true; };

    row.appendChild(upBtn);
    row.appendChild(downBtn);

    // 3 Dots Context Menu
    const dotsWrapper = document.createElement("div");
    dotsWrapper.className = "dots-menu-wrapper";
    
    const dotsBtn = document.createElement("button");
    dotsBtn.className = "action-icon-btn";
    dotsBtn.title = "More Options";
    dotsBtn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>`;
    
    const dropdown = document.createElement("div");
    dropdown.className = "dots-dropdown";
    dropdown.innerHTML = `
      <button class="dots-option feedback-modal-btn">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
        Provide Feedback
      </button>
    `;

    dotsBtn.onclick = (e) => {
      e.stopPropagation();
      closeAllDotsMenus();
      dropdown.classList.toggle("show");
    };

    dotsWrapper.appendChild(dotsBtn);
    dotsWrapper.appendChild(dropdown);
    row.appendChild(dotsWrapper);
    
    if (sourceArticle) {
      const sourceLink = document.createElement("a");
      sourceLink.className = "action-source-link";
      sourceLink.href = sourceArticle.url;
      sourceLink.target = "_blank";
      sourceLink.innerHTML = `<svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="margin-right:4px;"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>${sourceArticle.title}`;
      sourceLink.title = "View Source";
      row.appendChild(sourceLink);
    }

    dropdown.querySelector(".feedback-modal-btn").onclick = () => {
      openFeedbackModal(payload);
      dropdown.classList.remove("show");
    };

    if (payload.intent === "disambiguation") {
      const disambigDiv = document.createElement("div");
      disambigDiv.className = "disambig-options";
      disambigDiv.style.cssText = "display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; margin-bottom:6px;";

      const options = (payload.context === "awaiting_mtop_type")
        ? [
            { label: "1️⃣ New MTOP", val: "1" },
            { label: "2️⃣ Renewal", val: "2" },
            { label: "3️⃣ Annual Permit", val: "3" },
            { label: "4️⃣ Dropping", val: "4" },
            { label: "5️⃣ Substitution", val: "5" },
            { label: "6️⃣ Transfer", val: "6" }
          ]
        : [
            { label: "1️⃣ New Business Permit", val: "1" },
            { label: "2️⃣ Renewal of Permit", val: "2" },
            { label: "3️⃣ Retirement of Permit", val: "3" },
            { label: "4️⃣ Transfer / Change Location", val: "4" }
          ];

      options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "btn-secondary btn-sm";
        btn.style.cssText = "font-size:12px; padding:6px 14px; border-radius:20px; cursor:pointer; background:var(--accent1, #2563eb); color:white; border:none; font-weight:500; transition:transform 0.15s ease;";
        btn.textContent = opt.label;
        btn.onclick = () => quickAsk(opt.val);
        disambigDiv.appendChild(btn);
      });
      row.appendChild(disambigDiv);
    }

    if (payload.intent === "unresolved" || payload.intent === "missing_intent") {
      const recoveryDiv = document.createElement("div");
      recoveryDiv.className = "fallback-recovery-actions";
      recoveryDiv.style.cssText = "display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; margin-bottom:6px;";
      
      const dirBtn = document.createElement("button");
      dirBtn.className = "btn-secondary btn-sm";
      dirBtn.style.cssText = "font-size:12px; padding:6px 14px; border-radius:20px; cursor:pointer; background:var(--accent1, #2563eb); color:white; border:none; display:inline-flex; align-items:center; gap:6px; font-weight:500;";
      dirBtn.innerHTML = `🏢 Open Office Directory`;
      dirBtn.onclick = () => {
        showView("services");
        if (typeof window.switchServiceTab === "function") window.switchServiceTab("directory");
      };
      recoveryDiv.appendChild(dirBtn);

      const suggestions = ["Business Permit", "Birth Certificate", "Real Property Tax"];
      suggestions.forEach(s => {
        const chip = document.createElement("button");
        chip.className = "btn-secondary btn-sm";
        chip.style.cssText = "font-size:12px; padding:6px 12px; border-radius:20px; cursor:pointer; background:var(--surface, #f1f5f9); color:var(--text, #1e293b); border:1px solid var(--border, #cbd5e1);";
        chip.textContent = s;
        chip.onclick = () => quickAsk(s);
        recoveryDiv.appendChild(chip);
      });

      row.appendChild(recoveryDiv);
    }
  }

  const meta = content.querySelector(".meta");
  if (meta) {
    content.insertBefore(row, meta);
  } else {
    content.appendChild(row);
  }
}

export async function submitFeedback(payload, helpful, comment = null) {
  try {
    await fetch(`${API_URL}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: payload.question,
        answer: payload.answer,
        intent: payload.intent,
        helpful,
        language: payload.language,
        comment: comment
      })
    });

    if (comment) {
      showToast("Thanks for your detailed feedback!");
    } else {
      showToast(helpful ? "Thanks for your feedback!" : "We'll improve that.");
    }
  } catch (error) {
    console.error(error);
  }
}

let currentFeedbackPayload = null;
export function openFeedbackModal(payload) {
  currentFeedbackPayload = payload;
  const overlay = document.getElementById("feedbackModalOverlay");
  const textarea = document.getElementById("feedbackCommentText");
  if (overlay) overlay.classList.add("show");
  if (textarea) {
    textarea.value = "";
    setTimeout(() => textarea.focus(), 150);
  }
}

export function bindFeedbackModal() {
    const submitBtn = document.getElementById("submitFeedbackBtn");
    if (submitBtn) {
      submitBtn.addEventListener("click", () => {
        const textarea = document.getElementById("feedbackCommentText");
        const comment = textarea.value.trim();
        if (comment && currentFeedbackPayload) {
          submitFeedback(currentFeedbackPayload, false, comment);
          closeFeedbackModal();
        } else {
          showToast("Please type a comment before submitting.");
        }
      });
    }
}

/* ==================== RELATED ARTICLES ==================== */
export function addRelatedArticlesToMessage(msgElement, articles) {
  const content = msgElement.querySelector(".msg-content");
  if (!content) return;

  const filtered = (articles || []).filter(a => a.score > 0.01);
  if (!filtered.length) return;

  const wrapper = document.createElement("div");
  wrapper.className = "message-related-articles";
  wrapper.innerHTML = `<div class="related-label">Related Articles:</div>`;
  
  const chips = document.createElement("div");
  chips.className = "related-chips";

  filtered.forEach(article => {
    if (article.url) {
      const item = document.createElement("a");
      item.className = "related-chip-link";
      item.href = article.url;
      item.target = "_blank";
      item.textContent = article.title;
      chips.appendChild(item);
    } else {
      const item = document.createElement("button");
      item.className = "related-chip-btn";
      item.textContent = article.title;
      item.onclick = () => quickAsk(article.title);
      chips.appendChild(item);
    }
  });

  wrapper.appendChild(chips);
  content.appendChild(wrapper);
}

/* ==================== AUTOCOMPLETE ==================== */
const autocompleteSuggestions = [
  "How to apply for a business permit?",
  "What are the requirements for a birth certificate?",
  "How to pay real property tax?",
  "Where is the BPLO office located?",
  "How to renew my business permit?",
  "Can I pay my taxes online?",
  "What is the contact number for the Mayor's office?",
  "Steps for building permit application",
  "How to get a marriage license?",
  "Process for retirement of business permit",
  "How to get a certificate of no marriage (CENOMAR)?",
  "What are the working hours of the municipal hall?"
];

export function initAutocomplete() {
  const input = document.getElementById("user-input");
  const dropdown = document.getElementById("autocompleteDropdown");
  if (!input || !dropdown) return;

  input.addEventListener("input", (e) => {
    const val = e.target.value.trim().toLowerCase();
    dropdown.innerHTML = "";
    
    if (!val) {
      dropdown.classList.remove("show");
      return;
    }

    const matches = autocompleteSuggestions.filter(s => s.toLowerCase().includes(val));
    
    if (matches.length > 0) {
      matches.slice(0, 5).forEach(match => {
        const item = document.createElement("div");
        item.className = "autocomplete-item";
        const regex = new RegExp(`(${val})`, "gi");
        item.innerHTML = match.replace(regex, "<strong>$1</strong>");
        
        item.addEventListener("mousedown", (ev) => {
          ev.preventDefault(); 
          input.value = match;
          input.dispatchEvent(new Event("input", { bubbles: true }));
          dropdown.classList.remove("show");
          input.focus();
        });
        dropdown.appendChild(item);
      });
      dropdown.classList.add("show");
    } else {
      dropdown.classList.remove("show");
    }
  });

  input.addEventListener("blur", () => {
    dropdown.classList.remove("show");
  });

  input.addEventListener("focus", (e) => {
    if (e.target.value.trim()) {
      input.dispatchEvent(new Event("input"));
    }
  });
}
