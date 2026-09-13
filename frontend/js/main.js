import { state } from './state.js';
import { 
  bindTheme, applyTheme, initSettings, initLanguage, 
  bindSidebar, applySidebarCollapse, bindMobileMenu, 
  bindGlobalClick, openPrivacyModal, closePrivacyModal 
} from './ui.js';
import { 
  listenAuthState, bindAuth, bindPhoneCountry, 
  bindOTPInputs, bindPhoneInputValidation, bindEditProfileModal,
  checkEmailSignInLink
} from './auth.js';
import { 
  initVoiceInput 
} from './voice.js';
import { 
  clearChat, initAutocomplete, handleKey, sendMessage, 
  startNewChat, bindFeedbackModal 
} from './chat.js';
import { 
  bindHistoryTabs, loadHistoryForUser, renderHistory, 
  confirmClearHistory, clearArchived 
} from './history.js';
import { 
  switchServiceTab, loadDynamicGuide, loadDynamicDirectory 
} from './services.js';
import { timeNow } from './utils.js';

// Expose some functions globally for HTML inline handlers
window.quickAsk = (q) => import('./chat.js').then(module => module.quickAsk(q));
window.quickAskAndGo = (q) => import('./chat.js').then(module => module.quickAskAndGo(q));
window.sendMessage = () => import('./chat.js').then(module => module.sendMessage());
window.switchServiceTab = switchServiceTab;

// Bind missing modal and auth functions used by inline HTML onclicks
window.openPrivacyModal = openPrivacyModal;
window.closePrivacyModal = closePrivacyModal;
window.closeModal = () => document.getElementById("modalOverlay")?.classList.remove("show");
window.closeFeedbackModal = () => document.getElementById("feedbackModalOverlay")?.classList.remove("show");
window.confirmClearHistory = confirmClearHistory;
window.clearArchived = clearArchived;
window.closeLoginModal = () => document.getElementById("loginModalOverlay")?.classList.remove("show");
window.toggleAuthMode = () => {
    const emailForm = document.getElementById("emailLoginForm");
    const phoneForm = document.getElementById("phoneLoginForm");
    const modeLabel = document.getElementById("authModeLabel");
    if(emailForm && emailForm.style.display !== "none") {
        emailForm.style.display = "none";
        if(phoneForm) phoneForm.style.display = "flex";
        if(modeLabel) modeLabel.textContent = "Continue with Email";
    } else {
        if(phoneForm) phoneForm.style.display = "none";
        if(emailForm) emailForm.style.display = "flex";
        if(modeLabel) modeLabel.textContent = "Continue with Phone";
    }
};
window.performEmailLogin = async () => { const { performEmailLogin } = await import('./auth.js'); performEmailLogin(); };
window.performPhoneLogin = async () => { const { performPhoneLogin } = await import('./auth.js'); performPhoneLogin(); };
window.verifyOTP = async () => { const { verifyOTP } = await import('./auth.js'); verifyOTP(); };
window.resendOTP = async () => { const { resendOTP } = await import('./auth.js'); resendOTP(); };
window.resetLoginModal = async () => { const { resetLoginModal } = await import('./auth.js'); resetLoginModal(); };

document.addEventListener("DOMContentLoaded", () => {
  // 1. Theme & UI Settings
  applyTheme(state.theme);
  bindTheme();
  initSettings();
  initLanguage();
  applySidebarCollapse();
  bindSidebar();
  bindMobileMenu();
  bindGlobalClick();
  
  // 2. Auth & User Profile
  listenAuthState();
  bindAuth();
  bindPhoneCountry();
  bindOTPInputs();
  bindPhoneInputValidation();
  bindEditProfileModal();
  checkEmailSignInLink();
  
  // 3. Chat & Voice
  initVoiceInput();
  initAutocomplete();
  
  // Bind Send Button and Enter Key
  const sendBtn = document.querySelector(".send-btn");
  if(sendBtn) sendBtn.addEventListener("click", sendMessage);
  
  const userInput = document.getElementById("user-input");
  if(userInput) userInput.addEventListener("keydown", handleKey);
  
  const newChatBtn = document.getElementById("newChatBtn");
  if(newChatBtn) newChatBtn.addEventListener("click", startNewChat);

  // 4. History
  bindHistoryTabs();
  
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");
  if(clearHistoryBtn) clearHistoryBtn.addEventListener("click", confirmClearHistory);
  
  const clearArchivedBtn = document.getElementById("clearArchivedBtn");
  if(clearArchivedBtn) clearArchivedBtn.addEventListener("click", clearArchived);
  
  // 5. Modals
  bindFeedbackModal();
  
  const privacyPolicyBtn = document.getElementById("privacyPolicyBtn");
  if(privacyPolicyBtn) privacyPolicyBtn.addEventListener("click", openPrivacyModal);
  
  const privacyCloseBtn = document.getElementById("privacyCloseBtn");
  if(privacyCloseBtn) privacyCloseBtn.addEventListener("click", closePrivacyModal);
  
  const privacyModalOverlay = document.getElementById("privacyModalOverlay");
  if(privacyModalOverlay) privacyModalOverlay.addEventListener("click", (e) => {
    if (e.target === privacyModalOverlay) closePrivacyModal();
  });
  
  // 6. Dynamic Content Loading
  loadDynamicGuide();
  loadDynamicDirectory();
  
  // Update time display
  const sysTimeEl = document.getElementById("sysTime");
  if(sysTimeEl) sysTimeEl.textContent = timeNow();
  
  // Initialize initial empty state properly
  if(!state.currentSessionId || state.currentMessages.length === 0) {
    clearChat();
  }
});
