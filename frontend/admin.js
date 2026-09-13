const API_URL = "http://127.0.0.1:8001";

async function adminFetch(url, options = {}) {
  options.headers = options.headers || {};
  const token = sessionStorage.getItem("vista_admin_token");
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  return fetch(url, options);
}


// Auth credentials managed via backend


/* ==================== STATE */
const adminState = {
  theme: localStorage.getItem("vista_admin_theme") || "light",
  authenticated: sessionStorage.getItem("vista_admin_auth") === "true",
  authenticated: sessionStorage.getItem("vista_admin_auth") === "true",
  unmatchedData: [],
  feedbackData: [],
  knowledgeData: [],
  chatLogsData: [],
  intentToDelete: null
};

let analyticsChartInstance = null;

/* ==================== ADMIN AUTH GATE */
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

function hideAdminGate() {
  const gate = document.getElementById("adminLoginGate");
  gate.style.opacity = "0";
  gate.style.visibility = "hidden";
  gate.style.pointerEvents = "none";
  setTimeout(() => { gate.style.display = "none"; }, 300);
}

function initAdminAuth() {
  const gate = document.getElementById("adminLoginGate");
  const submitBtn = document.getElementById("adminLoginSubmit");
  const passwordInput = document.getElementById("adminPassword");

  if (adminState.authenticated) {
    hideAdminGate();
    return;
  }

  submitBtn.addEventListener("click", handleAdminLogin);
  passwordInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleAdminLogin();
  });
}

async function handleAdminLogin() {
  const passwordInput = document.getElementById("adminPassword");
  const errorEl = document.getElementById("adminLoginError");
  const submitBtn = document.getElementById("adminLoginSubmit");
  const password = passwordInput.value.trim();

  if (!password) {
    errorEl.textContent = "Please enter the administrator password.";
    errorEl.style.display = "block";
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Verifying...";

  try {
    const res = await fetch(`${API_URL}/api/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password })
    });
    const data = await res.json();

    if (data.status === "success") {
      adminState.authenticated = true;
      sessionStorage.setItem("vista_admin_auth", "true");
      sessionStorage.setItem("vista_admin_token", data.token);
      hideAdminGate();
    } else {
      errorEl.textContent = "Incorrect password. Please try again.";
      errorEl.style.display = "block";
      passwordInput.value = "";
      passwordInput.focus();
    }
  } catch (err) {
    errorEl.textContent = "Failed to connect to server.";
    errorEl.style.display = "block";
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg> Sign In`;
  }
}

/* ==================== INIT */
document.addEventListener("DOMContentLoaded", () => {
  applyTheme(adminState.theme);
  initAdminAuth();
  initNavigation();
  initMobileSidebar();
  initThemeToggle();
  loadStats();
  loadUnmatched();
  loadFeedback();
  loadIntents();
  loadAnalytics();
  loadChatLogs();
  loadDirectory();
  checkServerHealth();

  document.getElementById("retrainBtn").addEventListener("click", handleRetrain);
  document.getElementById("closeModalBtn").addEventListener("click", closeModal);
  document.getElementById("cancelBtn").addEventListener("click", closeModal);
  document.getElementById("addIntentForm").addEventListener("submit", handleAddIntent);
  document.getElementById("autoTranslateAllBtn")?.addEventListener("click", handleAutoTranslate);
  document.getElementById("exportDataBtn").addEventListener("click", handleExportData);
  document.getElementById("confirmDeleteBtn").addEventListener("click", confirmDelete);
  document.getElementById("changePasswordForm")?.addEventListener("click", (e) => {
    // Only bind on submit if the form actually submitted properly via button type submit
  });
  document.getElementById("changePasswordForm")?.addEventListener("submit", handleChangePassword);

  // Interaction Logs bindings
  const interactionSearch = document.getElementById("interactionSearch");
  if (interactionSearch) {
    interactionSearch.addEventListener("input", (e) => {
      filterChatLogs(e.target.value);
      filterFeedback(e.target.value);
    });
  }

  const clearAllInteractionBtn = document.getElementById("clearAllInteractionBtn");
  if (clearAllInteractionBtn) {
    clearAllInteractionBtn.addEventListener("click", () => {
      const activeTab = document.querySelector("#interactionlogs .htab.active").id;
      if (activeTab === "tab-btn-chatlogs") {
        handleClearChatLogs();
      } else {
        handleClearFeedback();
      }
    });
  }

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      sessionStorage.removeItem("vista_admin_auth");
      location.reload();
    });
  }

  // Search bindings
  document.getElementById("unmatchedSearch").addEventListener("input", filterUnmatched);
  document.getElementById("knowledgeSearch").addEventListener("input", filterKnowledge);
});

/* ==================== THEME */
function initThemeToggle() {
  const desktopBtn = document.getElementById("desktopThemeBtn");
  const mobileBtn = document.getElementById("mobileThemeBtn");

  if (desktopBtn) desktopBtn.addEventListener("click", toggleTheme);
  if (mobileBtn) mobileBtn.addEventListener("click", toggleTheme);
}

function toggleTheme() {
  const next = adminState.theme === "dark" ? "light" : "dark";
  applyTheme(next);
}

function applyTheme(theme) {
  adminState.theme = theme;
  localStorage.setItem("vista_admin_theme", theme);
  document.body.classList.remove("light-theme", "dark-theme");
  document.body.classList.add(theme + "-theme");

  const label = document.getElementById("themeLabel");
  const mobileBtn = document.getElementById("mobileThemeBtn");
  if (label) label.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
  if (mobileBtn) mobileBtn.textContent = theme === "dark" ? "☀️" : "🌙";
  
  // Re-render chart to update colors if initialized
  if (analyticsChartInstance) {
    loadAnalytics();
  }
}

/* ==================== MOBILE SIDEBAR */
function initMobileSidebar() {
  const menuBtn = document.getElementById("mobileMenuBtn");
  const overlay = document.getElementById("sidebarOverlay");

  if (menuBtn) menuBtn.addEventListener("click", toggleMobileSidebar);
  if (overlay) overlay.addEventListener("click", closeMobileSidebar);

  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) closeMobileSidebar();
  });
}

function toggleMobileSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
  document.getElementById("sidebarOverlay").classList.toggle("show");
}

function closeMobileSidebar() {
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebarOverlay").classList.remove("show");
}

/* ==================== NAVIGATION */
const pageTitles = {
  overview: { title: "Overview", subtitle: "Monitor your VISTA system at a glance" },
  knowledge: { title: "Knowledge Base", subtitle: "Manage intents, questions, and answers" },
  unmatched: { title: "Unmatched Queries", subtitle: "Review queries that VISTA couldn't answer" },
  interactionlogs: { title: "Interaction Logs", subtitle: "View all citizen-chatbot interactions and user feedback" }
};

function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const sections = document.querySelectorAll(".view-section");

  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      navItems.forEach(nav => nav.classList.remove("active"));
      item.classList.add("active");

      const targetId = item.getAttribute("data-target");
      sections.forEach(sec => sec.classList.remove("active"));
      document.getElementById(targetId).classList.add("active");

      const info = pageTitles[targetId] || {};
      document.getElementById("pageTitle").textContent = info.title || targetId;
      document.getElementById("pageSubtitle").textContent = info.subtitle || "";

      closeMobileSidebar();
    });
  });
}

/* ==================== SERVER HEALTH */
async function checkServerHealth() {
  const apiEl = document.getElementById("healthApi");
  const modelEl = document.getElementById("healthModel");
  const statusPill = document.getElementById("serverStatus");
  const accuracyEl = document.getElementById("healthAccuracy");
  const intentCountEl = document.getElementById("healthIntentCount");
  const lastTrainedEl = document.getElementById("healthLastTrained");

  try {
    const res = await fetch(`${API_URL}/health`);
    const data = await res.json();
    if (data.status === "ok") {
      if (apiEl) { apiEl.textContent = "Operational"; apiEl.className = "health-badge online"; }
      if (modelEl) { modelEl.textContent = "Loaded"; modelEl.className = "health-badge online"; }
      if (accuracyEl) { accuracyEl.textContent = data.accuracy + "%"; }
      if (intentCountEl) { intentCountEl.textContent = data.intent_count + " Intents Loaded"; }
      if (lastTrainedEl) { lastTrainedEl.textContent = data.last_trained || "—"; }
    }
  } catch {
    if (apiEl) { apiEl.textContent = "Offline"; apiEl.className = "health-badge offline"; }
    if (modelEl) { modelEl.textContent = "Unavailable"; modelEl.className = "health-badge offline"; }
    if (accuracyEl) { accuracyEl.textContent = "—"; accuracyEl.className = "health-badge offline"; }
    if (intentCountEl) { intentCountEl.textContent = "—"; }
    if (lastTrainedEl) { lastTrainedEl.textContent = "—"; }
    if (statusPill) {
      statusPill.innerHTML = '<span class="status-dot" style="background:var(--danger);animation:pulse 2s infinite"></span><span>System Offline</span>';
      statusPill.style.background = "var(--danger-light)";
      statusPill.style.color = "var(--danger)";
    }
  }
}

/* ==================== STATS */
async function loadStats() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/stats`);
    const data = await res.json();
    animateValue("stat-total", 0, data.total_queries, 800);
    animateValue("stat-unresolved", 0, data.unresolved_count, 800);
    animateValue("stat-feedback", 0, data.feedback_count, 800);
  } catch (err) {
    console.error("Failed to load stats", err);
  }
}

/* ==================== ANALYTICS ==================== */
async function loadAnalytics() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/analytics`);
    const data = await res.json();
    
    document.getElementById("analyticsBadge").textContent = data.type;
    document.getElementById("analyticsDesc").textContent = data.description;
    
    const ctx = document.getElementById("analyticsChart").getContext("2d");
    
    if (analyticsChartInstance) {
      analyticsChartInstance.destroy();
    }
    
    const isDark = adminState.theme === "dark";
    const textColor = isDark ? "#94a3b8" : "#64748b";
    const gridColor = isDark ? "#334155" : "#e2e8f0";

    const formatLabel = (label) => {
      if (!label) return "";
      return label.split('_')
        .filter(word => word.length > 0)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };
    const formattedLabels = data.labels.map(formatLabel);

    analyticsChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: formattedLabels.length ? formattedLabels : ["No Data"],
        datasets: [{
          label: "Inquiries",
          data: data.data.length ? data.data : [0],
          backgroundColor: "#3b82f6",
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: textColor, precision: 0, stepSize: 1 },
            grid: { color: gridColor }
          },
          x: {
            ticks: { color: textColor },
            grid: { display: false }
          }
        }
      }
    });
  } catch (err) {
    console.error("Failed to load analytics", err);
  }
}

/* ==================== KNOWLEDGE BASE ==================== */
async function loadIntents() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/intents`);
    adminState.knowledgeData = await res.json();
    renderKnowledge(adminState.knowledgeData);
  } catch (err) {
    console.error("Failed to load intents", err);
    renderEmptyTable("knowledge-tbody", 4, "Unable to load intents.");
  }
}

function renderKnowledge(data) {
  const tbody = document.getElementById("knowledge-tbody");
  tbody.innerHTML = "";

  if (!data.length) {
    renderEmptyTable("knowledge-tbody", 4, "Knowledge base is empty.");
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${escapeHtml(item.intent)}</strong></td>
      <td><span class="badge" style="background:var(--gray-200);color:var(--gray-800)">${escapeHtml(item.department)}</span></td>
      <td>${escapeHtml(item.en_question || "No sample question")}</td>
      <td>
        <div style="display:flex;gap:0.5rem">
          <button class="btn primary small" onclick="openEditModal('${escapeHtml(item.intent)}')">Edit</button>
          <button class="btn secondary small" style="color:var(--danger);border-color:var(--danger)" onclick="openDeleteModal('${escapeHtml(item.intent)}')">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function filterKnowledge() {
  const q = document.getElementById("knowledgeSearch").value.toLowerCase();
  const filtered = adminState.knowledgeData.filter(item =>
    item.intent.toLowerCase().includes(q) || 
    (item.en_question && item.en_question.toLowerCase().includes(q)) ||
    item.department.toLowerCase().includes(q)
  );
  renderKnowledge(filtered);
}

/* ==================== UNMATCHED */
async function loadUnmatched() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/unresolved`);
    adminState.unmatchedData = await res.json();
    renderUnmatched(adminState.unmatchedData);
  } catch (err) {
    console.error("Failed to load unmatched", err);
    renderEmptyTable("unmatched-tbody", 4, "Unable to load data. Is the server running?");
  }
}

function renderUnmatched(data) {
  const tbody = document.getElementById("unmatched-tbody");
  tbody.innerHTML = "";

  if (!data.length) {
    renderEmptyTable("unmatched-tbody", 4, "No unmatched queries found. Great job! 🎉");
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    const date = new Date(item.created_at).toLocaleDateString();
    const confClass = item.confidence < 0.4 ? "danger" : "warning";
    const confValue = (item.confidence * 100).toFixed(1) + "%";

    tr.innerHTML = `
      <td>${date}</td>
      <td><strong>${escapeHtml(item.question)}</strong></td>
      <td><span class="badge ${confClass}">${confValue}</span></td>
      <td>
        <div style="display:flex;gap:0.5rem">
          <button class="btn primary small resolve-btn" data-question="${escapeHtml(item.question)}">Resolve</button>
          <button class="btn secondary small dismiss-btn" style="color:var(--danger);border-color:var(--danger)" data-question="${escapeHtml(item.question)}">Dismiss</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.querySelectorAll(".resolve-btn").forEach(btn => {
    btn.addEventListener("click", (e) => openModal(e.target.getAttribute("data-question")));
  });

  document.querySelectorAll(".dismiss-btn").forEach(btn => {
    btn.addEventListener("click", (e) => dismissQuery(e.target.getAttribute("data-question")));
  });
}

async function dismissQuery(question) {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/unresolved/dismiss`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ Query dismissed.");
      loadUnmatched();
      loadStats();
    } else {
      showToast("❌ Failed to dismiss query.");
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Error connecting to server.");
  }
}

function filterUnmatched() {
  const q = document.getElementById("unmatchedSearch").value.toLowerCase();
  const filtered = adminState.unmatchedData.filter(item =>
    item.question.toLowerCase().includes(q)
  );
  renderUnmatched(filtered);
}

/* ==================== FEEDBACK */
async function loadFeedback() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/feedback`);
    adminState.feedbackData = await res.json();
    adminState.feedbackData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    renderFeedback(adminState.feedbackData);
  } catch (err) {
    console.error("Failed to load feedback", err);
    renderEmptyTable("feedback-tbody", 4, "Unable to load data. Is the server running?");
  }
}

function renderFeedback(data) {
  const tbody = document.getElementById("feedback-tbody");
  tbody.innerHTML = "";

  if (!data.length) {
    renderEmptyTable("feedback-tbody", 4, "No feedback entries yet.");
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    const date = new Date(item.created_at).toLocaleDateString();
    const badgeClass = item.helpful ? "success" : "danger";
    const badgeText = item.helpful ? "👍 Helpful" : "👎 Not Helpful";
    const escapedQuestion = escapeHtml(item.question);
    const escapedCreatedAt = escapeHtml(item.created_at);
    const escapedComment = item.comment ? escapeHtml(item.comment) : '<span style="color:var(--text-muted);font-style:italic;">None</span>';

    tr.innerHTML = `
      <td>${date}</td>
      <td>${escapedQuestion}</td>
      <td><span class="badge ${badgeClass}">${badgeText}</span></td>
      <td>${escapedComment}</td>
      <td><code style="font-size:12px;color:var(--text-muted)">${escapeHtml(item.intent)}</code></td>
      <td>
        <button class="btn secondary small feedback-delete-btn" style="color:var(--danger);border-color:var(--danger)" data-question="${escapedQuestion}" data-created="${escapedCreatedAt}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Bind delete buttons
  document.querySelectorAll(".feedback-delete-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const question = e.target.getAttribute("data-question");
      const created_at = e.target.getAttribute("data-created");
      handleDeleteFeedback(question, created_at);
    });
  });
}

function filterFeedback(query) {
  const q = (typeof query === "string" ? query : (document.getElementById("interactionSearch")?.value || "")).toLowerCase();
  const filtered = adminState.feedbackData.filter(item =>
    item.question.toLowerCase().includes(q) || item.intent.toLowerCase().includes(q)
  );
  renderFeedback(filtered);
}

/* ==================== EMPTY TABLE STATE */
function renderEmptyTable(tbodyId, colspan, message) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = `
    <tr>
      <td colspan="${colspan}">
        <div class="empty-table-state">
          <div class="empty-icon">📭</div>
          <p>${message}</p>
        </div>
      </td>
    </tr>
  `;
}

/* ==================== FEEDBACK DELETE/CLEAR ==================== */
async function handleDeleteFeedback(question, created_at) {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/feedback/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, created_at })
    });
    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ Feedback entry deleted.");
      loadFeedback();
      loadStats();
    } else {
      showToast("❌ Failed to delete feedback.");
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Error connecting to server.");
  }
}

async function handleClearFeedback() {
  if (!confirm("Are you sure you want to clear ALL feedback entries? This cannot be undone.")) return;
  try {
    const res = await adminFetch(`${API_URL}/api/admin/feedback/clear`, { method: "POST" });
    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ All feedback cleared.");
      loadFeedback();
      loadStats();
    } else {
      showToast("❌ Failed to clear feedback.");
    }
  } catch (err) {
    showToast("❌ Error connecting to server.");
  }
}

/* ==================== CHAT LOGS ==================== */
async function loadChatLogs() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/chat_logs`);
    adminState.chatLogsData = await res.json();
    renderChatLogs(adminState.chatLogsData);
  } catch (err) {
    console.error("Failed to load chat logs", err);
    renderEmptyTable("chatlogs-tbody", 5, "Unable to load chat logs. Is the server running?");
  }
}

function renderChatLogs(data) {
  const tbody = document.getElementById("chatlogs-tbody");
  tbody.innerHTML = "";

  if (!data.length) {
    renderEmptyTable("chatlogs-tbody", 5, "No chat logs recorded yet.");
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    const date = new Date(item.created_at).toLocaleString();
    const confValue = ((item.confidence || 0) * 100).toFixed(1) + "%";
    const confClass = (item.confidence || 0) >= 0.7 ? "success" : (item.confidence || 0) >= 0.35 ? "warning" : "danger";
    const langMap = { en: "English", tl: "Tagalog", bis: "Bisaya" };
    const langDisplay = langMap[item.language] || item.language || "Auto";

    tr.innerHTML = `
      <td style="white-space:nowrap">${date}</td>
      <td>${escapeHtml(item.question || "")}</td>
      <td><code style="font-size:12px;color:var(--text-muted)">${escapeHtml(item.intent || "")}</code></td>
      <td><span class="badge ${confClass}">${confValue}</span></td>
      <td><span class="badge" style="background:var(--gray-200);color:var(--gray-800)">${langDisplay}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function filterChatLogs(query) {
  const q = (typeof query === "string" ? query : (document.getElementById("interactionSearch")?.value || "")).toLowerCase();
  const filtered = adminState.chatLogsData.filter(item =>
    (item.question || "").toLowerCase().includes(q) ||
    (item.intent || "").toLowerCase().includes(q) ||
    (item.language || "").toLowerCase().includes(q)
  );
  renderChatLogs(filtered);
}

async function handleClearChatLogs() {
  if (!confirm("Are you sure you want to clear ALL chat logs? This cannot be undone.")) return;
  try {
    const res = await adminFetch(`${API_URL}/api/admin/chat_logs/clear`, { method: "POST" });
    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ All chat logs cleared.");
      loadChatLogs();
      loadStats();
      loadAnalytics();
    } else {
      showToast("❌ Failed to clear chat logs.");
    }
  } catch (err) {
    showToast("❌ Error connecting to server.");
  }
}

/* ==================== INTERACTION TABS ==================== */
function switchInteractionTab(tab) {
  const chatBtn = document.getElementById("tab-btn-chatlogs");
  const feedBtn = document.getElementById("tab-btn-feedback");
  const chatTab = document.getElementById("interactionTabChatlogs");
  const feedTab = document.getElementById("interactionTabFeedback");

  if (!chatBtn || !feedBtn || !chatTab || !feedTab) return;

  if (tab === "chatlogs") {
    chatBtn.classList.add("active");
    feedBtn.classList.remove("active");
    chatTab.style.display = "flex";
    feedTab.style.display = "none";
  } else {
    feedBtn.classList.add("active");
    chatBtn.classList.remove("active");
    chatTab.style.display = "none";
    feedTab.style.display = "flex";
  }
}

/* ==================== RETRAIN */
async function handleRetrain() {
  const btn = document.getElementById("retrainBtn");
  btn.disabled = true;
  btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="animation:spin 1s linear infinite"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg><span>Retraining...</span>`;

  try {
    const res = await adminFetch(`${API_URL}/api/admin/retrain`, { method: "POST" });
    const data = await res.json();
    if (data.status === "success") {
      showToast(`✅ Model retrained! Accuracy: ${(data.metrics.best_accuracy * 100).toFixed(1)}%`);
      checkServerHealth();
    } else {
      showToast(`❌ Error: ${data.message}`);
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Failed to connect to server.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg><span>Retrain Model</span>`;
  }
}

/* ==================== MODAL */
function openModal(question) {
  document.getElementById("resolveQueryText").value = question;
  populateResolveDropdown();
  document.getElementById("resolveModal").classList.add("active");
}

function closeResolveModal() {
  document.getElementById("resolveModal").classList.remove("active");
}

function populateResolveDropdown() {
  const select = document.getElementById("resolveExistingIntentSelect");
  select.innerHTML = '<option value="">-- Select an Intent --</option>';
  
  // Sort knowledge data alphabetically by intent name
  const sortedData = [...adminState.knowledgeData].sort((a, b) => a.intent.localeCompare(b.intent));
  
  sortedData.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item.intent;
    opt.textContent = `${item.intent} (${item.department || 'No Dept'})`;
    select.appendChild(opt);
  });
}

async function handleLinkIntent() {
  const question = document.getElementById("resolveQueryText").value;
  const intent = document.getElementById("resolveExistingIntentSelect").value;
  
  if (!intent) {
    showToast("⚠️ Please select an intent to link this query to.");
    return;
  }
  
  try {
    const payload = { question, intent };
    const res = await adminFetch(`${API_URL}/api/admin/unresolved/link`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ Query successfully linked to intent!");
      closeResolveModal();
      loadUnmatched();
      loadStats();
    } else {
      showToast(`❌ Error: ${data.message}`);
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Failed to connect to server.");
  }
}

function handleCreateNewFromResolve() {
  const question = document.getElementById("resolveQueryText").value;
  closeResolveModal();
  openAddModal();
  document.getElementById("add-en-question").value = question;
}

function populateDatalists() {
  const intents = new Set();
  const departments = new Set();
  const tags = new Set();

  adminState.knowledgeData.forEach(item => {
    if (item.intent) intents.add(item.intent);
    if (item.department) departments.add(item.department);
    if (item.tags) {
      item.tags.split(',').forEach(t => {
        if (t.trim()) tags.add(t.trim());
      });
    }
  });

  const intentList = document.getElementById("intent-list");
  const deptList = document.getElementById("department-list");
  const tagsList = document.getElementById("tags-list");
  
  if(intentList) intentList.innerHTML = Array.from(intents).map(i => `<option value="${i}">`).join("");
  if(deptList) deptList.innerHTML = Array.from(departments).map(d => `<option value="${d}">`).join("");
  if(tagsList) tagsList.innerHTML = Array.from(tags).map(t => `<option value="${t}">`).join("");
}

function openAddModal() {
  document.getElementById("modalMode").value = "add";
  document.getElementById("editIntentId").value = "";
  document.getElementById("intentModalTitle").textContent = "Add to Knowledge Base";
  document.getElementById("addIntentForm").reset();
  populateDatalists();
  document.getElementById("addIntentModal").classList.add("active");
}

function openEditModal(intentId) {
  const intent = adminState.knowledgeData.find(i => i.intent === intentId);
  if(!intent) return;
  
  document.getElementById("modalMode").value = "edit";
  document.getElementById("editIntentId").value = intentId;
  document.getElementById("intentModalTitle").textContent = "Edit Intent";
  
  // Populate form
  document.getElementById("add-en-question").value = intent.en_question || "";
  document.getElementById("add-intent").value = intent.intent;
  document.getElementById("add-department").value = intent.department || "";
  document.getElementById("add-tags").value = intent.tags || "";
  document.getElementById("add-tl-question").value = intent.tl_question || "";
  document.getElementById("add-bis-question").value = intent.bis_question || "";
  document.getElementById("add-en-answer").value = intent.en_answer || "";
  document.getElementById("add-tl-answer").value = intent.tl_answer || "";
  document.getElementById("add-bis-answer").value = intent.bis_answer || "";
  
  populateDatalists();
  document.getElementById("addIntentModal").classList.add("active");
}

function closeModal() {
  document.getElementById("addIntentModal").classList.remove("active");
  document.getElementById("addIntentForm").reset();
}

function openDeleteModal(intentId) {
  adminState.intentToDelete = intentId;
  document.getElementById("deleteModal").classList.add("active");
}

function closeDeleteModal() {
  adminState.intentToDelete = null;
  document.getElementById("deleteModal").classList.remove("active");
}

function openProfileModal() {
  document.getElementById("profileModal").classList.add("active");
}

function closeProfileModal() {
  document.getElementById("profileModal").classList.remove("active");
}

/* ==================== CHANGE PASSWORD ==================== */
function openChangePasswordModal() {
  document.getElementById("changePasswordForm").reset();
  document.getElementById("changePasswordModal").classList.add("active");
}

function closeChangePasswordModal() {
  document.getElementById("changePasswordModal").classList.remove("active");
}

async function handleChangePassword(e) {
  e.preventDefault();
  const oldPwd = document.getElementById("cpOldPassword").value;
  const newPwd = document.getElementById("cpNewPassword").value;
  const confPwd = document.getElementById("cpConfirmPassword").value;

  if (newPwd !== confPwd) {
    showToast("❌ New passwords do not match.");
    return;
  }

  if (newPwd.length < 6) {
    showToast("❌ Password must be at least 6 characters.");
    return;
  }

  const btn = document.getElementById("cpSubmitBtn");
  btn.disabled = true;
  btn.textContent = "Updating...";

  try {
    const res = await adminFetch(`${API_URL}/api/admin/change_password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
    });
    const data = await res.json();
    
    if (data.status === "success") {
      showToast("✅ Administrator password changed successfully.");
      sessionStorage.setItem("vista_admin_token", newPwd); // update token
      closeChangePasswordModal();
      closeProfileModal();
    } else {
      showToast(`❌ Error: ${data.message}`);
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Failed to connect to server.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Update Password";
  }
}

async function confirmDelete() {
  const intentId = adminState.intentToDelete;
  if (!intentId) return;
  
  try {
    const res = await adminFetch(`${API_URL}/api/admin/intents/${intentId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ Intent deleted successfully.");
      closeDeleteModal();
      loadIntents();
    } else {
      showToast("❌ Failed to delete intent.");
    }
  } catch(err) {
    showToast("❌ Error connecting to server.");
  }
}

/* ==================== ADD / EDIT INTENT */
async function handleAddIntent(e) {
  e.preventDefault();

  const mode = document.getElementById("modalMode").value;
  const editId = document.getElementById("editIntentId").value;
  
  const payload = {
    en_question: document.getElementById("add-en-question").value,
    intent: document.getElementById("add-intent").value,
    department: document.getElementById("add-department").value,
    tags: document.getElementById("add-tags").value,
    tl_question: document.getElementById("add-tl-question").value,
    bis_question: document.getElementById("add-bis-question").value,
    en_answer: document.getElementById("add-en-answer").value,
    tl_answer: document.getElementById("add-tl-answer").value,
    bis_answer: document.getElementById("add-bis-answer").value,
  };

  const url = mode === "edit" ? `${API_URL}/api/admin/intents/${editId}` : `${API_URL}/api/admin/add_intent`;
  const method = mode === "edit" ? "PUT" : "POST";

  try {
    const res = await adminFetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ Knowledge Base updated!");
      closeModal();
      loadStats();
      loadUnmatched();
      loadIntents();
    } else {
      showToast("❌ Failed to save intent.");
    }
  } catch (err) {
    showToast("❌ Error connecting to server.");
  }
}

/* ==================== AUTO TRANSLATE */
async function handleAutoTranslate() {
  const enQuestion = document.getElementById("add-en-question").value.trim();
  const enAnswer = document.getElementById("add-en-answer").value.trim();
  
  if (!enQuestion && !enAnswer) {
    showToast("⚠️ Please enter English text first.");
    return;
  }
  
  const btn = document.getElementById("autoTranslateAllBtn");
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="animation:spin 1s linear infinite"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg> Translating...`;
  btn.disabled = true;

  try {
    let hasError = false;
    
    if (enQuestion) {
      const resQ = await adminFetch(`${API_URL}/api/admin/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: enQuestion })
      });
      const dataQ = await resQ.json();
      if (dataQ.status === "success") {
        document.getElementById("add-tl-question").value = dataQ.tl || "";
        document.getElementById("add-bis-question").value = dataQ.bis || "";
      } else {
        showToast("❌ " + dataQ.message);
        hasError = true;
      }
    }
    
    if (enAnswer) {
      const resA = await adminFetch(`${API_URL}/api/admin/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: enAnswer })
      });
      const dataA = await resA.json();
      if (dataA.status === "success") {
        document.getElementById("add-tl-answer").value = dataA.tl || "";
        document.getElementById("add-bis-answer").value = dataA.bis || "";
      } else {
        showToast("❌ " + dataA.message);
        hasError = true;
      }
    }
    
    if (!hasError) {
      showToast("✨ Translation complete!");
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Translation failed. Server might be down.");
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
  }
}

/* ==================== EXPORT */
function handleExportData() {
  const allData = [
    ...adminState.unmatchedData.map(d => ({
      type: "unmatched",
      question: d.question,
      confidence: d.confidence,
      date: d.created_at
    })),
    ...adminState.feedbackData.map(d => ({
      type: "feedback",
      question: d.question,
      intent: d.intent,
      helpful: d.helpful,
      date: d.created_at
    }))
  ];

  if (!allData.length) {
    showToast("📭 No data to export.");
    return;
  }

  const headers = ["type", "question", "confidence", "intent", "helpful", "date"];
  const csvRows = [headers.join(",")];

  allData.forEach(row => {
    const values = headers.map(h => {
      const val = row[h] ?? "";
      return `"${String(val).replace(/"/g, '""')}"`;
    });
    csvRows.push(values.join(","));
  });

  const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `vista_export_${new Date().toISOString().split("T")[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("📥 Data exported successfully!");
}

/* ==================== TOAST */
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 3500);
}

/* ==================== HELPERS */
function animateValue(id, start, end, duration) {
  if (start === end) { document.getElementById(id).textContent = end; return; }
  let startTime = null;
  const step = (ts) => {
    if (!startTime) startTime = ts;
    const progress = Math.min((ts - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    document.getElementById(id).textContent = Math.floor(eased * (end - start) + start);
    if (progress < 1) window.requestAnimationFrame(step);
  };
  window.requestAnimationFrame(step);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// CSS spin animation for retrain button
const style = document.createElement("style");
style.textContent = `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`;
document.head.appendChild(style);

/* ==================== DIRECTORY MANAGEMENT */
let directoryData = [];

async function loadDirectory() {
  try {
    const res = await adminFetch(`${API_URL}/api/offices`);
    const data = await res.json();
    if (!data.error) {
      directoryData = data;
      renderDirectory();
    }
  } catch (err) {
    console.error("Failed to load directory", err);
  }
}

function renderDirectory() {
  const tbody = document.getElementById("directory-tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  
  if (directoryData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:24px;">No offices found.</td></tr>`;
    return;
  }
  
  directoryData.forEach((office, index) => {
    const statusClass = office.status === "open" ? "status-resolved" : "status-unresolved";
    const statusText = office.status === "open" ? "Open" : "Closed";
    
    tbody.innerHTML += `
      <tr>
        <td style="font-weight:600;color:var(--text-color);">${escapeHtml(office.name || "Unknown")}</td>
        <td>
          <div style="font-size:13px;">${escapeHtml(office.location || "—")}</div>
          <div style="font-size:12px;color:var(--text-muted);">${escapeHtml(office.head || "—")}</div>
        </td>
        <td>
          <div style="font-size:13px;">${escapeHtml(office.phone || "—")}</div>
          <div style="font-size:12px;color:var(--text-muted);">${escapeHtml(office.email || "—")}</div>
        </td>
        <td><span class="status-badge ${statusClass}">${statusText}</span></td>
        <td>
          <div class="action-btns">
            <button class="icon-btn" title="Edit" onclick="openEditOfficeModal(${index})">✏️</button>
            <button class="icon-btn" style="color:var(--danger)" title="Delete" onclick="deleteOffice(${index})">🗑️</button>
          </div>
        </td>
      </tr>
    `;
  });
}

function openAddOfficeModal() {
  document.getElementById("officeForm").reset();
  document.getElementById("officeIndex").value = "-1";
  document.getElementById("officeModalTitle").textContent = "Add New Office";
  document.getElementById("officeModal").classList.add("active");
}

function openEditOfficeModal(index) {
  const office = directoryData[index];
  document.getElementById("officeIndex").value = index;
  document.getElementById("officeName").value = office.name || "";
  document.getElementById("officeLocation").value = office.location || "";
  document.getElementById("officeHead").value = office.head || "";
  document.getElementById("officePhone").value = office.phone || "";
  document.getElementById("officeEmail").value = office.email || "";
  document.getElementById("officeHours").value = office.hours || "";
  document.getElementById("officeStatus").value = office.status || "open";
  
  document.getElementById("officeModalTitle").textContent = "Edit Office";
  document.getElementById("officeModal").classList.add("active");
}

function closeOfficeModal() {
  document.getElementById("officeModal").classList.remove("active");
}

async function saveOfficeData(offices) {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/offices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(offices)
    });
    const result = await res.json();
    if (result.status === "success") {
      showToast("Directory saved successfully.");
      directoryData = offices;
      renderDirectory();
      closeOfficeModal();
    } else {
      alert("Error saving: " + result.message);
    }
  } catch (err) {
    alert("Connection error.");
  }
}

document.getElementById("officeForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const index = parseInt(document.getElementById("officeIndex").value, 10);
  
  const office = {
    name: document.getElementById("officeName").value.trim(),
    location: document.getElementById("officeLocation").value.trim(),
    head: document.getElementById("officeHead").value.trim(),
    phone: document.getElementById("officePhone").value.trim(),
    email: document.getElementById("officeEmail").value.trim(),
    hours: document.getElementById("officeHours").value.trim(),
    status: document.getElementById("officeStatus").value
  };
  
  const newDir = [...directoryData];
  if (index >= 0) {
    newDir[index] = office;
  } else {
    newDir.push(office);
  }
  
  saveOfficeData(newDir);
});

function deleteOffice(index) {
  if (!confirm(`Are you sure you want to delete ${directoryData[index].name}?`)) return;
  const newDir = directoryData.filter((_, i) => i !== index);
  saveOfficeData(newDir);
}
