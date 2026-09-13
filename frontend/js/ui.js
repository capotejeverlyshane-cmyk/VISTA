import { state } from './state.js';
import { showToast } from './utils.js';

export const newChatLabels = {
  auto: "New Chat",
  en: "New Chat",
  tl: "Bagong Chat",
  bis: "Bag-ong Chat"
};

export function updateNewChatLabel() {
  const label = document.getElementById("newChatLabel");
  if (label) label.textContent = newChatLabels[state.language] || newChatLabels.en;
}

/* ==================== THEME */
export function bindTheme() {
  const desktopBtn = document.getElementById("themeToggleDesktop");
  const mobileBtn = document.getElementById("themeToggleMobile");
  const darkToggle = document.getElementById("darkModeToggle");

  if (darkToggle) darkToggle.checked = state.theme === "dark";

  if (desktopBtn) {
    desktopBtn.addEventListener("click", () => {
      const next = state.theme === "dark" ? "light" : "dark";
      applyTheme(next);
      if (darkToggle) darkToggle.checked = next === "dark";
    });
  }

  if (mobileBtn) {
    mobileBtn.addEventListener("click", () => {
      const next = state.theme === "dark" ? "light" : "dark";
      applyTheme(next);
      if (darkToggle) darkToggle.checked = next === "dark";
    });
  }

  if (darkToggle) {
    darkToggle.addEventListener("change", () => {
      applyTheme(darkToggle.checked ? "dark" : "light");
    });
  }
}

export function applyTheme(theme) {
  state.theme = theme;
  localStorage.setItem("vista_theme", theme);
  document.body.classList.remove("light-theme", "dark-theme");
  document.body.classList.add(theme === "dark" ? "dark-theme" : "light-theme");

  const btn = document.getElementById("themeToggleDesktop");
  const mobileIcon = document.getElementById("themeMobileIcon");
  if (btn) {
    btn.innerHTML = theme === "dark" 
      ? `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`
      : `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>`;
  }
  if (mobileIcon) mobileIcon.textContent = theme === "dark" ? "☀" : "🌙";
}

/* ==================== SETTINGS */
export function initSettings() {
  const seniorToggle = document.getElementById("seniorModeToggle");
  const fontSel = document.getElementById("fontSizeSelect");
  const langSel = document.getElementById("langSettingSelect");
  const darkToggle = document.getElementById("darkModeToggle");
  const voiceReplyToggle = document.getElementById("voiceReplyToggle");

  if(seniorToggle) seniorToggle.checked = state.seniorMode;
  if(fontSel) fontSel.value = state.fontSize;
  if(langSel) langSel.value = state.language;
  if(darkToggle) darkToggle.checked = state.theme === "dark";
  if(voiceReplyToggle) voiceReplyToggle.checked = state.voiceReply;

  if(seniorToggle) seniorToggle.addEventListener("change", () => applySeniorMode(seniorToggle.checked));
  if(fontSel) fontSel.addEventListener("change", () => applyFontSize(fontSel.value));

  if(langSel) {
    langSel.addEventListener("change", () => {
        state.language = langSel.value;
        localStorage.setItem("vista_language", state.language);
        const langDropdown = document.getElementById("languageSelect");
        if (langDropdown) langDropdown.value = state.language;
        updateNewChatLabel();
        showToast("Language preference saved.");
    });
  }

  if(voiceReplyToggle) {
    voiceReplyToggle.addEventListener("change", () => {
        state.voiceReply = voiceReplyToggle.checked;
        localStorage.setItem("vista_voice_reply", JSON.stringify(state.voiceReply));
        showToast(state.voiceReply ? "Voice replies enabled." : "Voice replies disabled.");
    });
  }
}

export function applySeniorMode(enabled) {
  state.seniorMode = enabled;
  localStorage.setItem("vista_senior", JSON.stringify(enabled));
  document.body.classList.toggle("senior-mode", enabled);
  const toggle = document.getElementById("seniorModeToggle");
  if(toggle) toggle.checked = enabled;
}

export function applyFontSize(size) {
  state.fontSize = size;
  localStorage.setItem("vista_fontsize", size);
  document.body.classList.remove("font-large", "font-xlarge");
  if (size === "large") document.body.classList.add("font-large");
  if (size === "xlarge") document.body.classList.add("font-xlarge");
}

/* ==================== LANGUAGE */
export function initLanguage() {
  const sel = document.getElementById("languageSelect");
  if (sel) {
    sel.value = state.language;
    sel.addEventListener("change", () => {
      state.language = sel.value;
      localStorage.setItem("vista_language", state.language);
      const langSettingSelect = document.getElementById("langSettingSelect");
      if(langSettingSelect) langSettingSelect.value = state.language;
      updateNewChatLabel();
    });
  }
}

/* ==================== VIEW */
export function showView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  const target = document.getElementById(`view-${name}`);
  if (target) target.classList.add("active");
}

export function setActiveNav(name) {
  document.querySelectorAll(".nav-item").forEach(i => {
    i.classList.toggle("active", i.dataset.view === name);
  });
}

/* ==================== SIDEBAR */
export function bindSidebar() {
  document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      showView(item.dataset.view);
      closeSidebarMobile();
    });
  });

  const collapseSidebarBtn = document.getElementById("collapseSidebarBtn");
  if(collapseSidebarBtn) {
    collapseSidebarBtn.addEventListener("click", () => {
        state.sidebarCollapsed = !state.sidebarCollapsed;
        localStorage.setItem("vista_collapsed", JSON.stringify(state.sidebarCollapsed));
        applySidebarCollapse();
    });
  }
}

export function applySidebarCollapse() {
  if (window.innerWidth > 860) {
    const sidebar = document.getElementById("sidebar");
    if(sidebar) sidebar.classList.toggle("collapsed", state.sidebarCollapsed);
    const btn = document.getElementById("collapseSidebarBtn");
    if(btn) btn.textContent = state.sidebarCollapsed ? "⟩" : "⟨";
  }
}

export function bindMobileMenu() {
  const toggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");

  if(toggle) {
    toggle.addEventListener("click", () => {
        if(sidebar) sidebar.classList.toggle("open");
        if(overlay) overlay.classList.toggle("show");
    });
  }

  if(overlay) overlay.addEventListener("click", closeSidebarMobile);

  window.addEventListener("resize", () => {
    if (window.innerWidth > 860) {
      if(sidebar) sidebar.classList.remove("open");
      if(overlay) overlay.classList.remove("show");
      applySidebarCollapse();
    }
  });
}

export function closeSidebarMobile() {
  if (window.innerWidth <= 860) {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    if(sidebar) sidebar.classList.remove("open");
    if(overlay) overlay.classList.remove("show");
  }
}

/* ==================== GLOBAL CLICK */
export function bindGlobalClick() {
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".dots-menu-wrapper")) closeAllDotsMenus();
  });
}

export function closeAllDotsMenus() {
  document.querySelectorAll(".dots-dropdown.show").forEach(d => d.classList.remove("show"));
  state.openMenuId = null;
}

/* ==================== MODAL */
export function showModal(title, message, onConfirm) {
  const titleEl = document.getElementById("modalTitle");
  const msgEl = document.getElementById("modalMessage");
  const overlay = document.getElementById("modalOverlay");
  const confirmBtn = document.getElementById("modalConfirmBtn");

  if(titleEl) titleEl.textContent = title;
  if(msgEl) msgEl.textContent = message;
  state.modalCallback = onConfirm;
  if(overlay) overlay.classList.add("show");

  if(confirmBtn) {
    confirmBtn.onclick = () => {
        if (state.modalCallback) state.modalCallback();
        closeModal();
    };
  }
}

export function closeModal() {
  const overlay = document.getElementById("modalOverlay");
  if(overlay) overlay.classList.remove("show");
  state.modalCallback = null;
}

export function openPrivacyModal() {
  const overlay = document.getElementById("privacyModalOverlay");
  if(overlay) overlay.classList.add("show");
}

export function closePrivacyModal() {
  const overlay = document.getElementById("privacyModalOverlay");
  if(overlay) overlay.classList.remove("show");
}

export function closeFeedbackModal() {
  const overlay = document.getElementById("feedbackModalOverlay");
  if(overlay) overlay.classList.remove("show");
}
