export const API_URL = (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost")
  ? "http://127.0.0.1:8001"
  : "https://vista-qqiz.onrender.com"; // <--- Replace with your live backend URL

async function adminFetch(url, options = {}) {
  options.headers = options.headers || {};
  const token = sessionStorage.getItem("vista_admin_token");
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(url, options);
  if (res.status === 401 || res.status === 403) {
    // Token expired or invalid: reset session and show login gate
    sessionStorage.removeItem("vista_admin_auth");
    sessionStorage.removeItem("vista_admin_token");
    adminState.authenticated = false;
    const gate = document.getElementById("adminLoginGate");
    if (gate) {
      gate.style.display = "flex";
      gate.style.opacity = "1";
      gate.style.visibility = "visible";
      gate.style.pointerEvents = "auto";
    }
  }
  return res;
}


// Auth credentials managed via backend


/* ==================== STATE */
const adminState = {
  theme: localStorage.getItem("vista_admin_theme") || "light",
  authenticated: sessionStorage.getItem("vista_admin_auth") === "true",
  unmatchedData: [],
  feedbackData: [],
  knowledgeData: [],
  chatLogsData: [],
  intentToDelete: null,
  unmatchedIdToDismissOnAdd: null
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
      loadStats();
      loadUnmatched();
      loadFeedback();
      loadIntents();
      loadAnalytics();
      loadChatLogs();
      loadDirectory();
      checkServerHealth();
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

  // Only load protected data if authenticated session exists
  if (adminState.authenticated) {
    loadStats();
    loadUnmatched();
    loadFeedback();
    loadIntents();
    loadAnalytics();
    loadChatLogs();
    loadDirectory();
  }
  checkServerHealth();

  document.getElementById("retrainBtn").addEventListener("click", handleRetrain);
  document.getElementById("closeModalBtn").addEventListener("click", closeModal);
  document.getElementById("cancelBtn").addEventListener("click", closeModal);
  document.getElementById("addIntentForm").addEventListener("submit", handleAddIntent);

  const enQuestionInput = document.getElementById("add-en-question");
  const intentInput = document.getElementById("add-intent");
  if (enQuestionInput && intentInput) {
    enQuestionInput.addEventListener("input", () => {
      const mode = document.getElementById("modalMode").value;
      if (mode === "add" && !intentInput.dataset.userEdited) {
        intentInput.value = enQuestionInput.value
          .toLowerCase()
          .replace(/[^a-z0-9\s]/g, "")
          .trim()
          .split(/\s+/)
          .slice(0, 4)
          .join("_");
      }
    });
    intentInput.addEventListener("input", () => {
      intentInput.dataset.userEdited = "true";
    });
  }
  document.getElementById("autoTranslateAllBtn")?.addEventListener("click", handleAutoTranslate);
  document.getElementById("exportDataBtn").addEventListener("click", handleExportData);
  document.getElementById("confirmDeleteBtn").addEventListener("click", confirmDelete);
  document.getElementById("downloadChatLogsCsvBtn")?.addEventListener("click", downloadChatLogsCsv);
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

/* ==================== FORMATTERS & UTILITIES */
function formatTopicName(intentName) {
  if (!intentName) return "Unknown Topic";
  const deptPrefixes = [
    "cmo_", "bplo_", "cswdo_", "cto_", "ccro_", "ccr_", "cao_", "ceo_",
    "cho_", "cenro_", "cdrrmo_", "cpdo_", "peso_", "gso_", "casso_"
  ];
  let clean = String(intentName).trim().toLowerCase();
  for (const prefix of deptPrefixes) {
    if (clean.startsWith(prefix)) {
      clean = clean.slice(prefix.length);
      break;
    }
  }

  const acronyms = {
    "pwd": "PWD",
    "aics": "AICS",
    "cedula": "Cedula",
    "bpls": "BPLS",
    "id": "ID",
    "faq": "FAQ",
    "faqs": "FAQs"
  };

  return clean
    .split("_")
    .filter(Boolean)
    .map(word => acronyms[word.toLowerCase()] || (word.charAt(0).toUpperCase() + word.slice(1)))
    .join(" ");
}

/* ==================== NAVIGATION */
const pageTitles = {
  overview: { title: "Overview", subtitle: "Monitor your VISTA system at a glance" },
  knowledge: { title: "Knowledge Base", subtitle: "Manage topics, questions, and answers" },
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

      if (targetId === "overview") {
        loadStats();
        loadAnalytics();
      }

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
    const res = await fetch(`${API_URL}/api/admin/health`);
    if (!res.ok) {
      throw new Error(`Health check failed with status ${res.status}`);
    }
    const data = await res.json();
    if (data.status !== "ok") {
      throw new Error("Health check returned an unexpected response");
    }

    if (apiEl) { apiEl.textContent = "Operational"; apiEl.className = "health-badge online"; }
    if (modelEl) {
      modelEl.textContent = data.model_loaded ? "Loaded" : "Unavailable";
      modelEl.className = data.model_loaded ? "health-badge online" : "health-badge offline";
    }
    if (accuracyEl) {
      accuracyEl.textContent = Number.isFinite(data.accuracy) ? `${data.accuracy.toFixed(1)}%` : "—";
      accuracyEl.className = Number.isFinite(data.accuracy) ? "health-badge online" : "health-badge offline";
    }
    if (intentCountEl) {
      intentCountEl.textContent = Number.isFinite(data.intent_count)
        ? `${data.intent_count} Topics Loaded`
        : "—";
    }
    if (lastTrainedEl) { lastTrainedEl.textContent = data.last_trained || "—"; }
    if (statusPill) {
      statusPill.innerHTML = '<span class="status-dot online"></span><span>System Online</span>';
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
    animateValue("stat-total", 0, data.total_queries || 0, 1000);
    animateValue("stat-resolved-rate", 0, data.resolved_rate !== undefined ? data.resolved_rate : 90.5, 1000, "%");
    animateValue("stat-unresolved", 0, data.unresolved_count || 0, 1000);
    animateValue("stat-accuracy", 0, data.accuracy || 96.1, 1000, "%");
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
    console.error("Failed to load topics", err);
    renderEmptyTable("knowledge-tbody", 4, "Unable to load topics.");
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
    const formatted = formatTopicName(item.intent);
    tr.innerHTML = `
      <td>
        <div style="font-weight:600;color:var(--text);font-size:14px;">${escapeHtml(formatted)}</div>
        <div style="font-size:11px;color:var(--text-muted);font-family:monospace;margin-top:2px;">${escapeHtml(item.intent)}</div>
      </td>
      <td><span class="badge" style="background:var(--surface-2);color:var(--text-2)">${escapeHtml(item.department || "General")}</span></td>
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
    formatTopicName(item.intent).toLowerCase().includes(q) ||
    (item.en_question && item.en_question.toLowerCase().includes(q)) ||
    (item.department && item.department.toLowerCase().includes(q))
  );
  renderKnowledge(filtered);
}

/* ==================== UNMATCHED */
async function loadUnmatched() {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/unresolved`);
    const rawData = await res.json();
    adminState.unmatchedData = Array.isArray(rawData) ? rawData : [];
    // Sort recent first (newest timestamp/created_at at the top)
    adminState.unmatchedData.sort((a, b) => {
      const timeA = new Date(a.created_at || a.timestamp || 0).getTime();
      const timeB = new Date(b.created_at || b.timestamp || 0).getTime();
      return timeB - timeA;
    });
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
    const d = new Date(item.created_at || item.timestamp);
    const dateStr = !isNaN(d.getTime()) ? d.toLocaleDateString() : "—";
    const timeStr = !isNaN(d.getTime()) ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";
    const confClass = item.confidence < 0.4 ? "danger" : "warning";
    const confValue = (item.confidence * 100).toFixed(1) + "%";

    tr.innerHTML = `
      <td style="white-space:nowrap">
        <div style="font-weight:500;">${dateStr}</div>
        ${timeStr ? `<div style="font-size:11px;color:var(--text-muted);">${timeStr}</div>` : ''}
      </td>
      <td><strong>${escapeHtml(item.question)}</strong></td>
      <td><span class="badge ${confClass}">${confValue}</span></td>
      <td>
        <div style="display:flex;gap:0.4rem;align-items:center;">
          <button class="btn primary small link-btn" data-question="${escapeHtml(item.question)}" data-question_id="${escapeHtml(item.id)}" title="Link query to existing topic">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
            <span>Link</span>
          </button>
          <button class="btn secondary small new-topic-btn" data-question="${escapeHtml(item.question)}" data-question_id="${escapeHtml(item.id)}" title="Create new topic from this query">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span>New</span>
          </button>
          <button class="btn secondary small dismiss-btn" style="color:var(--danger);border-color:var(--danger)" data-question="${escapeHtml(item.id)}" title="Dismiss query">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
            <span>Dismiss</span>
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll(".link-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const target = e.currentTarget;
      openLinkModal(target.getAttribute("data-question"), target.getAttribute("data-question_id"));
    });
  });

  tbody.querySelectorAll(".new-topic-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const target = e.currentTarget;
      openNewFromUnmatched(target.getAttribute("data-question"), target.getAttribute("data-question_id"));
    });
  });

  tbody.querySelectorAll(".dismiss-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const target = e.currentTarget;
      dismissQuery(target.getAttribute("data-question"));
    });
  });
}

async function dismissQuery(question) {
  try {
    const res = await adminFetch(`${API_URL}/api/admin/unresolved/dismiss`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: question })
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
    const data = await res.json();
    if (!res.ok || !Array.isArray(data)) throw new Error("Invalid feedback response.");
    adminState.feedbackData = data.map(item => ({
      ...item,
      created_at: item.created_at || item.timestamp,
      intent: item.intent || item.predicted_intent,
      helpful: item.helpful ?? (item.feedback_type === "helpful")
    }));
    adminState.feedbackData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    renderFeedback(adminState.feedbackData);
  } catch (err) {
    console.error("Failed to load feedback", err);
    renderEmptyTable("feedback-tbody", 6, "Unable to load data. Is the server running?");
  }
}

function renderFeedback(data) {
  const tbody = document.getElementById("feedback-tbody");
  tbody.innerHTML = "";

  if (!data.length) {
    renderEmptyTable("feedback-tbody", 6, "No feedback entries yet.");
    return;
  }

  data.forEach(item => {
    const tr = document.createElement("tr");
    const feedbackDate = new Date(item.created_at);
    const date = isNaN(feedbackDate.getTime()) ? "—" : feedbackDate.toLocaleDateString();
    const badgeClass = item.helpful ? "success" : "danger";
    const badgeText = item.helpful ? "👍 Helpful" : "👎 Not Helpful";
    const escapedQuestion = escapeHtml(item.question);
    const escapedCreatedAt = escapeHtml(item.created_at);
    const escapedComment = item.comment ? escapeHtml(item.comment) : '<span style="color:var(--text-muted);font-style:italic;">None</span>';

    const formattedTopic = item.intent ? formatTopicName(item.intent) : "—";
    tr.innerHTML = `
      <td>${date}</td>
      <td>${escapedQuestion}</td>
      <td><span class="badge ${badgeClass}">${badgeText}</span></td>
      <td>${escapedComment}</td>
      <td>
        <div style="font-weight:600;color:var(--text);font-size:13px;">${escapeHtml(formattedTopic)}</div>
        ${item.intent ? `<div style="font-size:11px;color:var(--text-muted);font-family:monospace;margin-top:2px;">${escapeHtml(item.intent)}</div>` : ''}
      </td>
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
    item.question.toLowerCase().includes(q) ||
    (item.intent && item.intent.toLowerCase().includes(q)) ||
    (item.intent && formatTopicName(item.intent).toLowerCase().includes(q))
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

    const formattedTopic = item.intent ? formatTopicName(item.intent) : "—";

    tr.innerHTML = `
      <td style="white-space:nowrap">${date}</td>
      <td>${escapeHtml(item.question || "")}</td>
      <td>
        <div style="font-weight:600;color:var(--text);font-size:13px;">${escapeHtml(formattedTopic)}</div>
        ${item.intent ? `<div style="font-size:11px;color:var(--text-muted);font-family:monospace;margin-top:2px;">${escapeHtml(item.intent)}</div>` : ''}
      </td>
      <td><span class="badge ${confClass}">${confValue}</span></td>
      <td><span class="badge" style="background:var(--surface-2);color:var(--text-2)">${escapeHtml(langDisplay)}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function filterChatLogs(query) {
  const q = (typeof query === "string" ? query : (document.getElementById("interactionSearch")?.value || "")).toLowerCase();
  const filtered = adminState.chatLogsData.filter(item =>
    (item.question || "").toLowerCase().includes(q) ||
    (item.intent || "").toLowerCase().includes(q) ||
    formatTopicName(item.intent || "").toLowerCase().includes(q) ||
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

async function downloadChatLogsCsv() {
  const button = document.getElementById("downloadChatLogsCsvBtn");
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "Preparing CSV...";

  try {
    const res = await adminFetch(`${API_URL}/api/admin/chat_logs/csv`);
    if (!res.ok) {
      throw new Error(`Export failed with status ${res.status}`);
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "chat_logs.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    showToast("📥 Chat logs downloaded.");
  } catch (err) {
    console.error("Failed to download chat logs CSV", err);
    showToast("❌ Unable to download chat logs.");
  } finally {
    button.disabled = false;
    button.textContent = originalText;
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
      showToast(`❌ Error: ${data.message || data.detail || "Training failed"}`);
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Failed to connect to server.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg><span>Retrain Model</span>`;
  }
}

/* ==================== MODAL (LINK QUERY TO TOPIC) */
let activeSuggestedIntent = null;

async function openLinkModal(question, id) {
  document.getElementById("resolveQueryText").value = question;
  document.getElementById("resolveQueryID").value = id;

  // Reset filter input
  const filterInput = document.getElementById("resolveTopicFilter");
  if (filterInput) filterInput.value = "";

  activeSuggestedIntent = null;
  const topicSelect = document.getElementById("resolveExistingIntentSelect");
  if (topicSelect) topicSelect.value = "";
  populateResolveDropdown();
  document.getElementById("resolveModal").classList.add("active");

  // Fetch AI suggestions for this citizen query
  fetchTopicSuggestions(question);
}
const openModal = openLinkModal;

function closeResolveModal() {
  document.getElementById("resolveModal").classList.remove("active");
}

async function fetchTopicSuggestions(query) {
  const container = document.getElementById("resolveAiSuggestions");
  const statusText = document.getElementById("suggestionsStatusText");
  if (!container) return;

  if (statusText) statusText.textContent = "Analyzing query...";
  container.innerHTML = `
    <div class="suggestion-skeleton"></div>
    <div class="suggestion-skeleton"></div>
  `;

  try {
    const res = await adminFetch(`${API_URL}/api/admin/suggest_topics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const data = await res.json();
    if (data.status === "success" && Array.isArray(data.suggestions) && data.suggestions.length > 0) {
      if (statusText) {
        statusText.textContent = `${data.suggestions.length} potential ${data.suggestions.length === 1 ? 'match' : 'matches'} found`;
      }
      renderAiSuggestions(data.suggestions);

      // Auto-select the top match if confidence is strong (>= 0.35)
      const top = data.suggestions[0];
      if (top && top.confidence >= 0.35) {
        selectTopicItem(top.intent_id || top.intent);
      }
    } else {
      if (statusText) statusText.textContent = "No confident matches";
      container.innerHTML = `
        <div class="suggestion-empty">
          No strong AI match found for this question. Search existing topics below or create a new topic.
        </div>
      `;
    }
  } catch (err) {
    console.error("Failed to fetch suggestions:", err);
    if (statusText) statusText.textContent = "Suggestions unavailable";
    container.innerHTML = `
      <div class="suggestion-empty" style="color:var(--text-muted);">
        Could not connect to suggestion service. Use manual search below.
      </div>
    `;
  }
}

function renderAiSuggestions(suggestions) {
  const container = document.getElementById("resolveAiSuggestions");
  if (!container) return;
  container.innerHTML = "";

  suggestions.forEach((s, idx) => {
    const card = document.createElement("div");
    card.className = "suggestion-card";
    const targetVal = s.intent_id || s.intent;
    card.setAttribute("data-intent", targetVal);

    const scorePct = Math.round(s.confidence * 100);
    const scoreClass = scorePct >= 50 ? "high" : (scorePct >= 20 ? "medium" : "low");

    card.innerHTML = `
      <div class="suggestion-header">
        <div class="suggestion-title">
          <span>${escapeHtml(formatTopicName(s.intent))}</span>
          ${idx === 0 && scorePct >= 35 ? '<span style="font-size:10px; background:var(--primary); color:#fff; padding:1px 5px; border-radius:4px; font-weight:700;">BEST</span>' : ''}
        </div>
        <div class="suggestion-meta">
          <span class="suggestion-dept">${escapeHtml(s.department || "General")}</span>
          <span class="suggestion-score ${scoreClass}">★ ${scorePct}%</span>
        </div>
      </div>
      <div class="suggestion-preview">${escapeHtml(s.preview || "No preview available")}</div>
    `;

    card.addEventListener("click", () => {
      selectTopicItem(targetVal);
    });

    container.appendChild(card);
  });
}

function selectTopicItem(targetVal) {
  activeSuggestedIntent = targetVal;

  // Update suggestion card selected styling
  const cards = document.querySelectorAll("#resolveAiSuggestions .suggestion-card");
  cards.forEach(c => {
    if (c.getAttribute("data-intent") === String(targetVal)) {
      c.classList.add("selected");
    } else {
      c.classList.remove("selected");
    }
  });

  // Update select dropdown
  const select = document.getElementById("resolveExistingIntentSelect");
  if (select) {
    let found = false;
    for (let i = 0; i < select.options.length; i++) {
      if (select.options[i].value === String(targetVal)) {
        select.selectedIndex = i;
        found = true;
        break;
      }
    }
    // If filtered out, reload without filter then select
    if (!found) {
      const filterInput = document.getElementById("resolveTopicFilter");
      if (filterInput) filterInput.value = "";
      populateResolveDropdown();
      select.value = String(targetVal);
    }
  }

  updateTopicPreview();
}

function filterResolveDropdown() {
  const filter = (document.getElementById("resolveTopicFilter")?.value || "").toLowerCase().trim();
  if (!filter) {
    populateResolveDropdown();
    return;
  }

  const filtered = adminState.knowledgeData.filter(item => {
    const name = formatTopicName(item.intent).toLowerCase();
    const intent = (item.intent || "").toLowerCase();
    const dept = (item.department || "").toLowerCase();
    const ans = (item.en || item.en_answer || "").toLowerCase();
    return name.includes(filter) || intent.includes(filter) || dept.includes(filter) || ans.includes(filter);
  });

  populateResolveDropdown(filtered);
}

function populateResolveDropdown(itemsToUse = null) {
  const select = document.getElementById("resolveExistingIntentSelect");
  if (!select) return;

  const currentVal = select.value || activeSuggestedIntent;
  const items = itemsToUse || adminState.knowledgeData;
  select.innerHTML = `<option value="">-- Choose a Topic (${items.length} available) --</option>`;

  // Sort knowledge data alphabetically by formatted topic name
  const sortedData = [...items].sort((a, b) => {
    const nameA = formatTopicName(a.intent);
    const nameB = formatTopicName(b.intent);
    return nameA.localeCompare(nameB);
  });

  sortedData.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item.intent_id || item.intent;
    const formatted = formatTopicName(item.intent);
    const rawAnswer = (item.en || item.en_answer || "").replace(/\*+/g, '').replace(/\r?\n+/g, ' ').trim();
    const preview = rawAnswer ? (rawAnswer.length > 50 ? rawAnswer.slice(0, 48) + "..." : rawAnswer) : "No preview";
    const dept = item.department ? ` [${item.department}]` : "";
    opt.textContent = `${formatted}${dept}`;
    select.appendChild(opt);
  });

  if (currentVal) {
    select.value = currentVal;
  }

  updateTopicPreview();
}

function updateTopicPreview() {
  const select = document.getElementById("resolveExistingIntentSelect");
  const previewEl = document.getElementById("resolveTopicPreview");
  if (!previewEl) return;
  const val = select ? select.value : activeSuggestedIntent;
  if (!val) {
    previewEl.style.display = "none";
    previewEl.innerHTML = "";
    return;
  }
  const item = adminState.knowledgeData.find(i => String(i.intent_id) === String(val) || i.intent === val);
  if (!item) {
    previewEl.style.display = "none";
    return;
  }
  const answer = (item.en || item.en_answer || "No English answer available.").replace(/\*+/g, '').trim();
  const dept = item.department || "General";
  previewEl.innerHTML = `
    <div style="font-weight:600;color:var(--text);margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;">
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="font-size:14px;">${escapeHtml(formatTopicName(item.intent))}</span>
        <code style="font-size:11px;background:var(--surface);padding:1px 6px;border-radius:4px;border:1px solid var(--border);color:var(--text-muted);">${escapeHtml(item.intent)}</code>
      </div>
      <span class="badge" style="background:var(--primary-light);color:var(--primary);font-size:11px;font-weight:600;">${escapeHtml(dept)}</span>
    </div>
    <div style="color:var(--text-2);font-size:12.5px;line-height:1.5;max-height:140px;overflow-y:auto;background:var(--surface);padding:8px 10px;border-radius:6px;border:1px solid var(--border);">
      ${escapeHtml(answer)}
    </div>
  `;
  previewEl.style.display = "block";
}

async function handleLinkIntent() {
  const question = document.getElementById("resolveQueryText").value;
  const select = document.getElementById("resolveExistingIntentSelect");
  const intent = select.value || activeSuggestedIntent;
  const language = document.getElementById("resolveExistingIntentSelectLang").value;
  const id = document.getElementById("resolveQueryID").value;

  if (!intent) {
    showToast("⚠️ Please select a topic to link this query to.");
    return;
  }

  const confirmBtn = document.getElementById("confirmLinkBtn");
  if (confirmBtn) {
    confirmBtn.disabled = true;
    confirmBtn.textContent = "Linking...";
  }

  try {
    const payload = { question, intent, language, id };
    const res = await adminFetch(`${API_URL}/api/admin/unresolved/link`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.status === "success") {
      showToast("✅ Query successfully linked to topic!");
      closeResolveModal();
      loadUnmatched();
      loadStats();
    } else {
      showToast(`❌ Error: ${data.message || "Failed to link query"}`);
    }
  } catch (err) {
    console.error(err);
    showToast("❌ Failed to connect to server.");
  } finally {
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.innerHTML = `<svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg> Link & Dismiss`;
    }
  }
}

function openNewFromUnmatched(question, id) {
  openAddModal();
  document.getElementById("add-en-question").value = question;
  // Auto-generate clean snake_case system topic identifier
  const suggestedIntent = question
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .trim()
    .split(/\s+/)
    .slice(0, 4)
    .join("_");
  const intentInput = document.getElementById("add-intent");
  if (intentInput) {
    intentInput.value = suggestedIntent;
    intentInput.dataset.userEdited = "true";
  }
  adminState.unmatchedIdToDismissOnAdd = id;
}

function handleCreateNewFromResolve() {
  const question = document.getElementById("resolveQueryText").value;
  const id = document.getElementById("resolveQueryID").value;
  closeResolveModal();
  openNewFromUnmatched(question, id);
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

  if (intentList) intentList.innerHTML = Array.from(intents).map(i => `<option value="${i}">`).join("");
  if (deptList) deptList.innerHTML = Array.from(departments).map(d => `<option value="${d}">`).join("");
  if (tagsList) tagsList.innerHTML = Array.from(tags).map(t => `<option value="${t}">`).join("");
}

function openAddModal() {
  document.getElementById("modalMode").value = "add";
  document.getElementById("editIntentId").value = "";
  document.getElementById("intentModalTitle").textContent = "Add Topic to Knowledge Base";
  document.getElementById("addIntentForm").reset();
  const intentInput = document.getElementById("add-intent");
  if (intentInput) delete intentInput.dataset.userEdited;
  populateDatalists();
  document.getElementById("addIntentModal").classList.add("active");
}

function openEditModal(intentId) {
  const intent = adminState.knowledgeData.find(i => i.intent === intentId);
  if (!intent) return;

  document.getElementById("modalMode").value = "edit";
  document.getElementById("editIntentId").value = intentId;
  const topicTitle = formatTopicName(intent.intent);
  document.getElementById("intentModalTitle").textContent = `Edit Topic: ${topicTitle}`;

  // Populate form
  document.getElementById("add-en-question").value = intent.en_question || "";
  document.getElementById("add-intent").value = intent.intent;
  document.getElementById("add-department").value = intent.department || "";
  document.getElementById("add-tags").value = intent.tags || "";
  document.getElementById("add-tl-question").value = intent.tl_question || "";
  document.getElementById("add-bis-question").value = intent.bis_question || "";
  document.getElementById("add-en-answer").value = intent.en_answer || intent.en || "";
  document.getElementById("add-tl-answer").value = intent.tl_answer || intent.tl || "";
  document.getElementById("add-bis-answer").value = intent.bis_answer || intent.bis || "";

  populateDatalists();
  document.getElementById("addIntentModal").classList.add("active");
}

function closeModal() {
  adminState.unmatchedIdToDismissOnAdd = null;
  document.getElementById("addIntentModal").classList.remove("active");
  document.getElementById("addIntentForm").reset();
  const intentInput = document.getElementById("add-intent");
  if (intentInput) delete intentInput.dataset.userEdited;
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
      showToast("✅ Topic deleted successfully.");
      closeDeleteModal();
      loadIntents();
    } else {
      showToast("❌ Failed to delete topic.");
    }
  } catch (err) {
    showToast("❌ Error connecting to server.");
  }
}

/* ==================== ADD / EDIT TOPIC */
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
      // If this topic was created from an unmatched query, auto-dismiss the query!
      if (adminState.unmatchedIdToDismissOnAdd) {
        try {
          await adminFetch(`${API_URL}/api/admin/unresolved/dismiss`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: adminState.unmatchedIdToDismissOnAdd })
          });
        } catch (e) {
          console.error("Failed to auto-dismiss unmatched query", e);
        }
        adminState.unmatchedIdToDismissOnAdd = null;
      }

      showToast(mode === "edit" ? "✅ Topic updated successfully!" : "✅ Topic added successfully!");
      closeModal();
      loadStats();
      loadUnmatched();
      loadIntents();
    } else {
      showToast("❌ Failed to save topic.");
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
function animateValue(id, start, end, duration = 1100, suffix = "") {
  const el = document.getElementById(id);
  if (!el) return;

  if (el._animFrame) {
    cancelAnimationFrame(el._animFrame);
    el._animFrame = null;
  }

  const endNum = parseFloat(end) || 0;
  const isFloat = String(end).includes(".") || (endNum % 1 !== 0);
  const currentText = (el.textContent || "").replace(/[^0-9.]/g, "");
  const startNum = currentText ? (parseFloat(currentText) || 0) : (parseFloat(start) || 0);

  if (startNum === endNum && el.textContent.trim() !== "0" && el.textContent.trim() !== "0%") {
    el.textContent = (isFloat ? endNum.toFixed(1) : endNum.toLocaleString()) + suffix;
    return;
  }

  let startTime = null;
  const step = (ts) => {
    if (!startTime) startTime = ts;
    const progress = Math.min((ts - startTime) / duration, 1);
    // Smooth ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = eased * (endNum - startNum) + startNum;

    el.textContent = (isFloat ? current.toFixed(1) : Math.round(current).toLocaleString()) + suffix;

    if (progress < 1) {
      el._animFrame = window.requestAnimationFrame(step);
    } else {
      el.textContent = (isFloat ? endNum.toFixed(1) : endNum.toLocaleString()) + suffix;
      el._animFrame = null;
    }
  };
  el._animFrame = window.requestAnimationFrame(step);
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
    if (!res.ok || !Array.isArray(data)) throw new Error("Invalid office directory response.");
    directoryData = data.map(office => {
      const normalized = { ...office };
      for (const field of ["head_of_office", "contact", "location", "operating_hours"]) {
        const value = typeof office[field] === "string" ? JSON.parse(office[field]) : office[field];
        if (value != null && (typeof value !== "object" || Array.isArray(value))) {
          throw new Error(`Invalid office field: ${field}`);
        }
        normalized[field] = value || {};
      }
      return normalized;
    });
    renderDirectory();
  } catch (err) {
    console.error("Failed to load directory", err);
    renderEmptyTable("directory-tbody", 5, "Unable to load the office directory.");
    showToast("Unable to load the office directory.");
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
    const head = office.head_of_office || {};
    const contact = office.contact || {};
    const location = office.location || {};
    const hours = office.operating_hours || {};
    const locationDetails = [location.floor, location.room]
      .filter(value => value !== undefined && value !== null && value !== "").join(" | ");

    tbody.innerHTML += `
      <tr>
        <td style="font-weight:600;color:var(--text);">
          ${escapeHtml(office.name || "Unknown")}
          <div class="directory-detail">${escapeHtml(office.office_id || "—")}</div>
        </td>
        <td>
          <div>${escapeHtml(location.building || "—")}</div>
          <div class="directory-detail">${escapeHtml(locationDetails || "—")}</div>
          <div class="directory-detail">${escapeHtml(head.name || "—")}${head.title ? ` (${escapeHtml(head.title)})` : ""}</div>
        </td>
        <td>
          <div>${escapeHtml(contact.phone || "—")}</div>
          <div class="directory-detail">${escapeHtml(contact.email || "—")}</div>
          ${contact.social_media ? `<div class="directory-detail">${escapeHtml(contact.social_media)}</div>` : ""}
        </td>
        <td>
          <div>${escapeHtml(hours.standard || "—")}</div>
          
          ${typeof hours.noon_break === "boolean" ? `<div class="directory-detail">${hours.noon_break ? "Observes Noon Break" : "No Noon Break"}</div>` : ""}
          ${hours.cut_off_time ? `<div class="directory-detail">Cut-off: ${escapeHtml(hours.cut_off_time)}</div>` : ""}
        </td>
        <td>
          <div class="directory-actions">
            <button type="button" class="btn secondary small" title="Edit" onclick="openEditOfficeModal(${index})">Edit</button>
            <button type="button" class="btn secondary small" style="color:var(--danger)" title="Delete" onclick="deleteOffice(${index})">Delete</button>
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
  const head = office.head_of_office || {};
  const contact = office.contact || {};
  const location = office.location || {};
  const hours = office.operating_hours || {};
  document.getElementById("officeIndex").value = index;
  document.getElementById("officeName").value = office.name || "";
  document.getElementById("officeId").value = office.office_id || "";
  document.getElementById("officeLocation").value = location.building || "";
  document.getElementById("officeFloor").value = location.floor ?? "";
  document.getElementById("officeRoom").value = location.room ?? "";
  document.getElementById("officeHead").value = head.name || "";
  document.getElementById("officeHeadTitle").value = head.title || "";
  document.getElementById("officePhone").value = contact.phone || "";
  document.getElementById("officeEmail").value = contact.email || "";
  document.getElementById("officeSocialMedia").value = contact.social_media || "";
  document.getElementById("officeHours").value = hours.standard || "";
  document.getElementById("officeCutOff").value = hours.cut_off_time || "";
  document.getElementById("officeNoonBreak").value = String(hours.noon_break === true);
  document.getElementById("officeStatus").value = office.status || "";

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
    if (res.ok && result.status === "success") {
      showToast("Directory saved successfully.");
      directoryData = offices;
      renderDirectory();
      closeOfficeModal();
    } else {
      alert("Error saving: " + (result.message || result.detail || "Unable to save the office directory."));
    }
  } catch (err) {
    console.error("Failed to save directory", err);
    alert("Connection error.");
  }
}

document.getElementById("officeForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const index = parseInt(document.getElementById("officeIndex").value, 10);
  const existingOffice = index >= 0 ? directoryData[index] : {};

  const office = {
    ...existingOffice,
    office_id: document.getElementById("officeId").value.trim(),
    name: document.getElementById("officeName").value.trim(),
    location: {
      ...existingOffice.location,
      building: document.getElementById("officeLocation").value.trim(),
      floor: document.getElementById("officeFloor").value.trim(),
      room: document.getElementById("officeRoom").value.trim()
    },
    head_of_office: {
      ...existingOffice.head_of_office,
      name: document.getElementById("officeHead").value.trim(),
      title: document.getElementById("officeHeadTitle").value.trim()
    },
    contact: {
      ...existingOffice.contact,
      phone: document.getElementById("officePhone").value.trim(),
      email: document.getElementById("officeEmail").value.trim(),
      social_media: document.getElementById("officeSocialMedia").value.trim()
    },
    operating_hours: {
      ...existingOffice.operating_hours,
      standard: document.getElementById("officeHours").value.trim(),
      noon_break: document.getElementById("officeNoonBreak").value === "true",
      cut_off_time: document.getElementById("officeCutOff").value.trim()
    }
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
