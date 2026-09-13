import { API_URL } from './config.js';
import { escapeHTML } from './utils.js';
import { quickAskAndGo } from './chat.js';

/* ==================== SERVICES TABS ==================== */
export function switchServiceTab(tab) {
  const guideBtn = document.getElementById("tab-btn-guide");
  const dirBtn = document.getElementById("tab-btn-directory");
  const guideTab = document.getElementById("serviceTabGuide");
  const dirTab = document.getElementById("serviceTabDirectory");

  if (!guideBtn || !dirBtn || !guideTab || !dirTab) return;

  if (tab === "guide") {
    guideBtn.classList.add("active");
    dirBtn.classList.remove("active");
    guideTab.style.display = "block";
    dirTab.style.display = "none";
  } else {
    dirBtn.classList.add("active");
    guideBtn.classList.remove("active");
    dirTab.style.display = "block";
    guideTab.style.display = "none";
  }
}

/* ==================== DYNAMIC SERVICE GUIDE ==================== */
const DEPT_ICONS = {
  "Civil Registrar": "📋", "BPLO": "🏪", "Treasurer's Office": "💰",
  "Engineering Office": "🏗️", "MSWD": "❤️", "Agriculture Office": "🌾",
  "Municipal Health Office": "🏥", "PESO": "💼", "MPDO": "📐",
  "MDRRMO": "🚒", "CMO": "🏛️", "SB Office": "📜",
  "Human Resources": "👥", "Budget Office": "📊", "General": "📁"
};

let allGuideServices = [];

export async function loadDynamicGuide() {
  const grid = document.getElementById("dynamicGuideGrid");
  if (!grid) return;
  try {
    const res = await fetch(`${API_URL}/api/services`);
    const data = await res.json();
    const departments = data.departments || {};

    allGuideServices = [];
    for (const [dept, services] of Object.entries(departments)) {
      services.forEach(svc => {
        allGuideServices.push({ ...svc, department: dept });
      });
    }

    renderGuideCards(allGuideServices);

    const searchInput = document.getElementById("guideSearchInput");
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        const q = searchInput.value.toLowerCase();
        const filtered = allGuideServices.filter(s =>
          s.display_name.toLowerCase().includes(q) ||
          s.department.toLowerCase().includes(q) ||
          s.intent.toLowerCase().includes(q)
        );
        renderGuideCards(filtered);
      });
    }
  } catch (err) {
    console.error("Failed to load service guide", err);
    grid.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted,#888);"><p>Unable to load services. Please ensure the backend server is running.</p></div>`;
  }
}

function renderGuideCards(services) {
  const grid = document.getElementById("dynamicGuideGrid");
  if (!grid) return;
  if (!services.length) {
    grid.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted,#888);"><p>No services match your search.</p></div>`;
    return;
  }

  // Group by department
  const grouped = {};
  services.forEach(svc => {
    if (!grouped[svc.department]) grouped[svc.department] = [];
    grouped[svc.department].push(svc);
  });

  const chevronSVG = `<svg class="chevron-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>`;
  const arrowSVG = `<svg class="svc-arrow" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>`;

  let html = '';
  for (const [dept, svcs] of Object.entries(grouped)) {
    if (dept.toLowerCase() === 'general') continue;
    const icon = DEPT_ICONS[dept] || '🏛️';
    let serviceItems = '';
    svcs.forEach(svc => {
      const question = `What is the process for ${svc.display_name}?`;
      serviceItems += `
        <div class="guide-service-item guide-service-btn" data-question="${escapeHTML(question)}" title="Ask about ${escapeHTML(svc.display_name)}">
          <span class="svc-name">${escapeHTML(svc.display_name)}</span>
          ${arrowSVG}
        </div>
      `;
    });

    html += `
      <div class="guide-accordion">
        <div class="guide-accordion-header guide-accordion-btn">
          <div class="dept-label">
            <span class="dept-emoji">${icon}</span>
            ${escapeHTML(dept)}
          </div>
          <div class="dept-meta">
            <span class="dept-count">${svcs.length} service${svcs.length !== 1 ? 's' : ''}</span>
            ${chevronSVG}
          </div>
        </div>
        <div class="guide-accordion-body">
          <div class="guide-service-list">
            ${serviceItems}
          </div>
        </div>
      </div>
    `;
  }
  grid.innerHTML = html;

  document.querySelectorAll('.guide-accordion-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        this.parentElement.classList.toggle('open');
    });
  });

  document.querySelectorAll('.guide-service-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        quickAskAndGo(this.getAttribute('data-question'));
    });
  });
}

/* ==================== DYNAMIC OFFICE DIRECTORY ==================== */
export async function loadDynamicDirectory() {
  const grid = document.getElementById("dynamicDirectoryGrid");
  if (!grid) return;
  try {
    const res = await fetch(`${API_URL}/api/offices`);
    const offices = await res.json();

    if (offices.error || !offices.length) {
      grid.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted,#888);"><p>No offices found.</p></div>`;
      return;
    }

    let html = '';
    const now = new Date();
    const currentHour = now.getHours();
    const isWeekend = now.getDay() === 0 || now.getDay() === 6;

    offices.forEach(office => {
      const icon = DEPT_ICONS[office.name] || '🏢';
      
      // Basic open/closed logic (8 AM to 5 PM)
      let isOpen = false;
      let statusText = "Closed";
      let statusClass = "status-closed";
      
      if (!isWeekend) {
        if (currentHour >= 8 && currentHour < 17) {
           isOpen = true;
           // Check noon break
           if (office.operating_hours.noon_break && currentHour === 12) {
             isOpen = false;
             statusText = "Noon Break";
           } else {
             statusText = "Open Now";
             statusClass = "status-open";
           }
        }
      }

      html += `
        <div class="directory-card premium-card">
          <div class="dir-header">
            <div class="dir-icon-large">${icon}</div>
            <div class="dir-title-area">
              <h3>${escapeHTML(office.name)}</h3>
              <div class="dir-status"><span class="status-dot ${statusClass}"></span> ${statusText}</div>
            </div>
          </div>
          
          <div class="dir-body">
            <div class="dir-info-row">
              <span class="dir-label">Head of Office</span>
              <span class="dir-value"><strong>${escapeHTML(office.head_of_office.name)}</strong>, ${escapeHTML(office.head_of_office.title)}</span>
            </div>
            <div class="dir-info-row">
              <span class="dir-label">Location</span>
              <span class="dir-value">${escapeHTML(office.location.building)}, ${escapeHTML(office.location.floor)}, ${escapeHTML(office.location.room)}</span>
            </div>
            <div class="dir-info-row">
              <span class="dir-label">Contact</span>
              <span class="dir-value contact-chips">
                <a href="tel:${escapeHTML(office.contact.phone)}" class="contact-chip">📞 ${escapeHTML(office.contact.phone)}</a>
                <a href="mailto:${escapeHTML(office.contact.email)}" class="contact-chip">✉️ Email</a>
              </span>
            </div>
            <div class="dir-info-row">
              <span class="dir-label">Hours</span>
              <span class="dir-value">${escapeHTML(office.operating_hours.standard)}
                ${office.operating_hours.noon_break ? '<br><small style="color:var(--danger)">Observes Noon Break</small>' : '<br><small style="color:var(--success)">No Noon Break</small>'}
              </span>
            </div>
          </div>
        </div>
      `;
    });
    grid.innerHTML = html;
  } catch (err) {
    console.error("Failed to load directory", err);
    grid.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted,#888);"><p>Unable to load directory. Please ensure the backend server is running.</p></div>`;
  }
}
