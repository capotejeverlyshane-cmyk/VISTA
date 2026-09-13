import { state } from './state.js';
import { truncate, showToast } from './utils.js';
import { renderCurrentChat, clearChat } from './chat.js';
import { showView, setActiveNav, closeSidebarMobile, closeAllDotsMenus, showModal } from './ui.js';

/* ==================== HISTORY */
export function getHistoryStorageKey() {
  return state.userId ? `vista_history_${state.userId}` : null;
}

export function loadHistoryForUser() {
  const key = getHistoryStorageKey();
  if (!key) {
    state.history = [];
    return;
  }
  const rawHistory = JSON.parse(localStorage.getItem(key) || "[]");
  state.history = rawHistory.map(item => {
    if (!item.messages || item.messages.length === 0) {
      item.messages = [{ role: "user", text: item.text || "Previous chat" }];
      if (item.answer) {
        item.messages.push({ role: "bot", text: item.answer });
      }
    }
    return item;
  });
}

export function persistHistory() {
  if (!state.loggedIn) return;
  const key = getHistoryStorageKey();
  if (!key) return;
  localStorage.setItem(key, JSON.stringify(state.history));
}

export function saveHistory() {
  if (!state.loggedIn || !state.currentSessionId || !state.currentMessages || state.currentMessages.length === 0) return;

  const existing = state.history.find(h => h.id.toString() === state.currentSessionId && !h.archived);
  if (existing) {
    existing.time = new Date().toLocaleString();
    existing.messages = [...state.currentMessages];
    existing.count = Math.floor(existing.messages.length / 2);
  } else {
    state.history.unshift({
      id: state.currentSessionId,
      text: state.currentMessages[0].text,
      messages: [...state.currentMessages],
      time: new Date().toLocaleString(),
      pinned: false,
      archived: false,
      count: 1
    });
  }

  state.history = state.history.slice(0, 30);
  persistHistory();
  renderHistory();
}

export function bindHistoryTabs() {
  document.querySelectorAll(".htab").forEach(tab => {
    tab.addEventListener("click", () => {
      // Only bind to history tabs
      if(!tab.parentElement.classList.contains("history-tabs") || tab.id.startsWith("tab-btn")) return;

      const parent = tab.closest('.history-tabs');
      if (parent) {
          parent.querySelectorAll(".htab").forEach(t => t.classList.remove("active"));
      }
      tab.classList.add("active");
      state.activeHistoryTab = tab.dataset.tab;
      renderHistory();
    });
  });

  const historySearch = document.getElementById("historySearch");
  if (historySearch) historySearch.addEventListener("input", renderHistory);
}

export function renderHistory() {
  const list = document.getElementById("historyList");
  if (!list) return;

  if (!state.loggedIn) {
    list.innerHTML = "";
    return;
  }

  const searchInput = document.getElementById("historySearch");
  const search = searchInput ? searchInput.value.toLowerCase() : "";
  const tab = state.activeHistoryTab;

  let items = state.history.filter(item => {
    const matchSearch = item.text.toLowerCase().includes(search);
    if (tab === "pinned") return item.pinned && !item.archived && matchSearch;
    if (tab === "archived") return item.archived && matchSearch;
    return !item.archived && matchSearch;
  });

  if (tab === "recent") {
    items = [...items].sort((a, b) => Number(b.pinned) - Number(a.pinned));
  }

  list.innerHTML = "";

  if (!items.length) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">${tab === "pinned" ? "📌" : tab === "archived" ? "🗃️" : "💬"}</div>
        <p>${tab === "pinned" ? "No pinned chats yet." : tab === "archived" ? "No archived chats." : "No recent chats yet."}</p>
      </div>
    `;
    return;
  }

  items.forEach(item => {
    const div = document.createElement("div");
    div.className = `recent-item${item.pinned ? " pinned" : ""}${item.archived ? " archived" : ""}`;

    div.innerHTML = `
      <div class="recent-item-text">
        <strong>${truncate(item.text, 28)}${item.pinned ? " 📌" : ""}</strong>
        <small>${item.time}</small>
      </div>
      <div class="dots-menu-wrapper">
        <button class="dots-btn" title="More options">⋯</button>
        <div class="dots-dropdown" id="dots-${item.id}">
          <button class="dots-option pin-btn">
            ${item.pinned ? "Unpin" : "Pin"}
          </button>
          <button class="dots-option archive-btn">
            ${item.archived ? "Unarchive" : "Archive"}
          </button>
          <button class="dots-option dots-delete delete-btn">
            Delete
          </button>
        </div>
      </div>
    `;

    const dotsBtn = div.querySelector(".dots-btn");
    dotsBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const dropdown = document.getElementById(`dots-${item.id}`);
      const isOpen = dropdown.classList.contains("show");
      closeAllDotsMenus();
      if (!isOpen) dropdown.classList.add("show");
    });

    const pinBtn = div.querySelector(".pin-btn");
    pinBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        togglePin(item.id);
    });

    const archiveBtn = div.querySelector(".archive-btn");
    archiveBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleArchive(item.id);
    });

    const deleteBtn = div.querySelector(".delete-btn");
    deleteBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteHistoryItem(item.id);
    });

    div.addEventListener("click", () => {
      showView("chat");
      setActiveNav("chat");
      closeSidebarMobile();
      // Restore the full conversation
      state.currentSessionId = item.id.toString();
      state.currentMessages = item.messages ? [...item.messages] : [];
      sessionStorage.setItem("vista_current_session", state.currentSessionId);
      sessionStorage.setItem("vista_current_messages", JSON.stringify(state.currentMessages));
      renderCurrentChat();
    });

    list.appendChild(div);
  });
}

function togglePin(id) {
  closeAllDotsMenus();
  const item = state.history.find(h => h.id === id);
  if (!item) return;
  item.pinned = !item.pinned;
  persistHistory();
  renderHistory();
  showToast(item.pinned ? "Chat pinned." : "Chat unpinned.");
}

function toggleArchive(id) {
  closeAllDotsMenus();
  const item = state.history.find(h => h.id === id);
  if (!item) return;
  item.archived = !item.archived;
  item.pinned = false;
  persistHistory();
  renderHistory();
  showToast(item.archived ? "Chat archived." : "Chat restored.");
}

function deleteHistoryItem(id) {
  closeAllDotsMenus();
  showModal("Delete this chat?", "This chat will be removed from your history.", () => {
    state.history = state.history.filter(h => h.id.toString() !== id.toString());
    persistHistory();
    renderHistory();
    showToast("Chat deleted.");
  });
}

export function confirmClearHistory() {
  if (!state.loggedIn) return showToast("Please log in first.");
  showModal("Clear All History?", "This will remove all saved conversations for this account on this device.", () => {
    state.history = [];
    persistHistory();
    renderHistory();
    showToast("Chat history cleared.");
  });
}

export function clearArchived() {
  if (!state.loggedIn) return showToast("Please log in first.");
  showModal("Clear Archived Chats?", "This will remove all archived conversations.", () => {
    state.history = state.history.filter(h => !h.archived);
    persistHistory();
    renderHistory();
    showToast("Archived chats cleared.");
  });
}
