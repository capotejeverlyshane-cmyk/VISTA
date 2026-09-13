import { state } from './state.js';
import { auth } from './config.js';
import { getInitials, isValidEmail, showToast } from './utils.js';
import { loadHistoryForUser, renderHistory, persistHistory } from './history.js';
import { clearChat, renderCurrentChat } from './chat.js';
import { showView, setActiveNav, closeSidebarMobile, showModal } from './ui.js';

/* ==================== AUTH STATE */
export function listenAuthState() {
  auth.onAuthStateChanged(async (user) => {
    if (user) {
      state.loggedIn = true;
      state.username = user.displayName || user.email?.split("@")[0] || user.phoneNumber || "User";
      state.userEmail = user.email || user.phoneNumber || "";
      state.userPhoto = user.photoURL || "";
      state.userId = user.uid;
      loadHistoryForUser();

      if (state.currentSessionId && (!state.currentMessages || state.currentMessages.length === 0)) {
        const recoveredItem = state.history.find(h => h.id.toString() === state.currentSessionId);
        if (recoveredItem && recoveredItem.messages && recoveredItem.messages.length > 0) {
          state.currentMessages = [...recoveredItem.messages];
          sessionStorage.setItem("vista_current_messages", JSON.stringify(state.currentMessages));
          renderCurrentChat();
        }
      }
    } else {
      state.loggedIn = false;
      state.username = "";
      state.userEmail = "";
      state.userPhoto = "";
      state.userId = "";
      state.history = [];
    }

    updateAuthUI();
    renderHistory();
  });
}

export function updateAuthUI() {
  const loggedOutEl = document.getElementById("authLoggedOut");
  const loggedInEl = document.getElementById("authLoggedIn");
  const historySection = document.getElementById("historySection");
  const historyLockedState = document.getElementById("historyLockedState");
  const historySettingsGroup = document.getElementById("historySettingsGroup");

  if (state.loggedIn) {
    if(loggedOutEl) loggedOutEl.style.display = "none";
    if(loggedInEl) loggedInEl.style.display = "block";
    if(historySection) historySection.style.display = "flex";
    if(historyLockedState) historyLockedState.style.display = "none";
    if(historySettingsGroup) historySettingsGroup.style.display = "block";

    const initials = getInitials(state.username);
    const userAvatarText = document.getElementById("userAvatarText");
    const userName = document.getElementById("userName");
    const userRole = document.getElementById("userRole");
    
    if(userAvatarText) userAvatarText.textContent = initials;
    if(userName) userName.textContent = state.username;
    if(userRole) userRole.textContent = state.userEmail || "Citizen Account";

    const popoverAvatar = document.getElementById("popoverAvatar");
    const popoverName = document.getElementById("popoverName");
    const popoverEmail = document.getElementById("popoverEmail");
    if (popoverAvatar) popoverAvatar.textContent = initials;
    if (popoverName) popoverName.textContent = state.username;
    if (popoverEmail) popoverEmail.textContent = state.userEmail || "Citizen Account";

    const welcomeTitle = document.getElementById("welcomeTitle");
    if (welcomeTitle) {
      const firstName = state.username.split(" ")[0];
      welcomeTitle.textContent = `How can I help you today, ${firstName}?`;
    }
  } else {
    if(loggedOutEl) loggedOutEl.style.display = "block";
    if(loggedInEl) loggedInEl.style.display = "none";
    if(historySection) historySection.style.display = "none";
    if(historyLockedState) historyLockedState.style.display = "block";
    if(historySettingsGroup) historySettingsGroup.style.display = "none";

    const welcomeTitle = document.getElementById("welcomeTitle");
    if (welcomeTitle) welcomeTitle.textContent = "How can I help you today?";
  }
}

/* ==================== ACCOUNT POPOVER */
export function toggleAccountPopover() {
  const popover = document.getElementById("accountPopover");
  if (!popover) return;
  if (popover.style.display === "block") {
    closeAccountPopover();
  } else {
    popover.style.display = "block";
  }
}

export function closeAccountPopover() {
  const popover = document.getElementById("accountPopover");
  if (popover) popover.style.display = "none";
}

/* ==================== EDIT PROFILE MODAL */
export function openEditProfileModal() {
  const overlay = document.getElementById("editProfileModalOverlay");
  if (!overlay) return;

  const avatarEl = document.getElementById("editProfileAvatar");
  const nameInput = document.getElementById("editDisplayName");
  const emailInput = document.getElementById("editEmail");

  if (avatarEl) avatarEl.textContent = getInitials(state.username);
  if (nameInput) nameInput.value = state.username || "";
  if (emailInput) emailInput.value = state.userEmail || "";

  overlay.classList.add("show");
}

export function closeEditProfileModal() {
  const overlay = document.getElementById("editProfileModalOverlay");
  if (overlay) overlay.classList.remove("show");
}

export function bindEditProfileModal() {
  const overlay = document.getElementById("editProfileModalOverlay");
  const closeBtn = document.getElementById("editProfileCloseBtn");
  const cancelBtn = document.getElementById("editProfileCancelBtn");
  const saveBtn = document.getElementById("editProfileSaveBtn");

  if (closeBtn) closeBtn.addEventListener("click", closeEditProfileModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeEditProfileModal);

  if (overlay) {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeEditProfileModal();
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      const nameInput = document.getElementById("editDisplayName");
      const newName = nameInput ? nameInput.value.trim() : "";
      if (!newName) return;

      state.username = newName;

      const initials = getInitials(newName);
      document.getElementById("userAvatarText").textContent = initials;
      document.getElementById("userName").textContent = newName;
      const popoverAvatar = document.getElementById("popoverAvatar");
      const popoverName = document.getElementById("popoverName");
      if (popoverAvatar) popoverAvatar.textContent = initials;
      if (popoverName) popoverName.textContent = newName;

      const welcomeTitle = document.getElementById("welcomeTitle");
      if (welcomeTitle) {
        const firstName = newName.split(" ")[0];
        welcomeTitle.textContent = `How can I help you today, ${firstName}?`;
      }

      closeEditProfileModal();
      showToast("Profile updated successfully!", "success");
    });
  }
}

/* ==================== AUTH BINDINGS */
export function bindAuth() {
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const userCard = document.getElementById("userCard");
  const loginEmail = document.getElementById("loginEmail");
  const googleLoginBtn = document.getElementById("googleLoginBtn");

  if (loginBtn) loginBtn.addEventListener("click", openLoginModal);

  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      performLogout();
      closeAccountPopover();
    });
  }

  if (userCard) {
    userCard.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleAccountPopover();
    });
  }

  const popoverSettingsBtn = document.getElementById("popoverSettingsBtn");
  if (popoverSettingsBtn) {
    popoverSettingsBtn.addEventListener("click", () => {
      closeAccountPopover();
      showView("settings");
      setActiveNav("settings");
      closeSidebarMobile();
    });
  }

  const popoverProfileBtn = document.getElementById("popoverProfileBtn");
  if (popoverProfileBtn) {
    popoverProfileBtn.addEventListener("click", () => {
      closeAccountPopover();
      openEditProfileModal();
    });
  }

  document.addEventListener("click", (e) => {
    const popover = document.getElementById("accountPopover");
    const card = document.getElementById("userCard");
    if (popover && popover.style.display === "block" && !popover.contains(e.target) && !card.contains(e.target)) {
      closeAccountPopover();
    }
  });

  if (loginEmail) {
    loginEmail.addEventListener("keydown", (e) => {
      if (e.key === "Enter") performEmailLogin();
    });
  }

  if (googleLoginBtn) googleLoginBtn.addEventListener("click", performGoogleLogin);
  
  const authModeToggleBtn = document.getElementById("authModeToggleBtn");
  if(authModeToggleBtn) authModeToggleBtn.addEventListener("click", toggleAuthMode);
  
  const emailContinueBtn = document.querySelector('#emailLoginForm .auth-continue-btn');
  if(emailContinueBtn) emailContinueBtn.addEventListener("click", performEmailLogin);
  
  const phoneLoginBtn = document.getElementById("phoneLoginBtn");
  if(phoneLoginBtn) phoneLoginBtn.addEventListener("click", performPhoneLogin);
  
  const verifyBtn = document.querySelector(".otp-section .auth-continue-btn");
  if(verifyBtn) verifyBtn.addEventListener("click", verifyOTP);
  
  const resendBtn = document.querySelector(".resend-btn");
  if(resendBtn) resendBtn.addEventListener("click", resendOTP);
  
  const backAuthBtn = document.querySelector(".back-auth-btn");
  if(backAuthBtn) backAuthBtn.addEventListener("click", resetLoginModal);
  
  const loginCloseBtn = document.querySelector(".login-close-btn");
  if(loginCloseBtn) loginCloseBtn.addEventListener("click", closeLoginModal);
}

/* ==================== GOOGLE */
export async function performGoogleLogin() {
  try {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope("email");
    provider.addScope("profile");
    const result = await auth.signInWithPopup(provider);
    closeLoginModal();
    showToast(`Welcome, ${result.user.displayName || "User"}!`);
  } catch (error) {
    console.error(error);
    showLoginError(error.message || "Google sign-in failed.");
  }
}

/* ==================== EMAIL MAGIC LINK */
export async function performEmailLogin() {
  const emailInput = document.getElementById("loginEmail");
  const continueBtn = document.querySelector('#emailLoginForm .auth-continue-btn');
  const email = emailInput?.value.trim() || "";

  if (!email) {
    showLoginError("Please enter your email address.");
    return;
  }

  if (!isValidEmail(email)) {
    showLoginError("Please enter a valid email address.");
    return;
  }

  try {
    hideLoginError();
    if (continueBtn) {
      continueBtn.disabled = true;
      continueBtn.textContent = "Sending...";
    }

    const actionCodeSettings = {
      url: window.location.origin + window.location.pathname,
      handleCodeInApp: true
    };

    await auth.sendSignInLinkToEmail(email, actionCodeSettings);
    localStorage.setItem("vista_email_for_signin", email);
    showToast(`Sign-in link sent to ${email}`);
    closeLoginModal();
  } catch (error) {
    console.error("Email login error:", error);
    showLoginError(error.message || "Unable to send sign-in link.");
  } finally {
    if (continueBtn) {
      continueBtn.disabled = false;
      continueBtn.textContent = "Continue";
    }
  }
}

export function checkEmailSignInLink() {
  if (auth.isSignInWithEmailLink(window.location.href)) {
    let email = localStorage.getItem("vista_email_for_signin");
    if (!email) email = prompt("Please confirm your email:");
    if (!email) return;

    auth.signInWithEmailLink(email, window.location.href)
      .then(() => {
        localStorage.removeItem("vista_email_for_signin");
        showToast("Successfully signed in!");
        window.history.replaceState({}, document.title, window.location.pathname);
      })
      .catch((error) => {
        console.error(error);
        showToast("Email sign-in failed.");
      });
  }
}

/* ==================== PHONE LOGIN */
export function bindPhoneCountry() {
  const countrySelect = document.getElementById("phoneCountry");
  const prefixEl = document.getElementById("phonePrefix");
  if (!countrySelect || !prefixEl) return;
  countrySelect.addEventListener("change", () => {
    prefixEl.textContent = countrySelect.value;
  });
}

export async function performPhoneLogin() {
  const countryCode = document.getElementById("phoneCountry")?.value || "+63";
  const phoneInput = document.getElementById("loginPhone");
  const continueBtn = document.getElementById("phoneLoginBtn");

  let phoneNumber = phoneInput?.value.trim() || "";
  phoneNumber = phoneNumber.replace(/\D/g, "");

  if (phoneInput) phoneInput.value = phoneNumber;

  if (!phoneNumber) {
    showLoginError("Please enter your phone number. Example: 9171234567");
    return;
  }

  if (countryCode === "+63") {
    if (phoneNumber.length === 11 && phoneNumber.startsWith("0")) {
      phoneNumber = phoneNumber.substring(1);
    }
    if (phoneNumber.length !== 10) {
      showLoginError("Philippine phone numbers must be 10 digits. Example: 9171234567");
      return;
    }
    if (!/^9\d{9}$/.test(phoneNumber)) {
      showLoginError("Please enter a valid Philippine mobile number. Example: 9171234567");
      return;
    }
  } else {
    if (phoneNumber.length < 7 || phoneNumber.length > 15) {
      showLoginError("Please enter a valid phone number.");
      return;
    }
  }

  const normalizedPhone = `${countryCode}${phoneNumber}`;

  try {
    hideLoginError();

    if (continueBtn) {
      continueBtn.disabled = true;
      continueBtn.textContent = "Sending...";
    }

    if (!window.recaptchaVerifier) {
      window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier("recaptcha-container", {
        size: "invisible"
      });
    }

    state.confirmationResult = await auth.signInWithPhoneNumber(normalizedPhone, window.recaptchaVerifier);

    const authMainActions = document.getElementById("authMainActions");
    const otpSection = document.getElementById("otpSection");

    if (authMainActions) authMainActions.style.display = "none";
    if (otpSection) otpSection.style.display = "block";

    const phoneDisplay = document.getElementById("otpPhoneDisplay");
    if (phoneDisplay) phoneDisplay.textContent = normalizedPhone;

    const firstOtp = document.querySelector('.otp-input[data-index="0"]');
    if (firstOtp) firstOtp.focus();

    showToast(`Verification code sent to ${normalizedPhone}`);
  } catch (error) {
    console.error("Phone login error:", error);
    showLoginError(error.message || "Phone sign-in failed.");
  } finally {
    if (continueBtn) {
      continueBtn.disabled = false;
      continueBtn.textContent = "Continue";
    }
  }
}

export function bindOTPInputs() {
  const inputs = document.querySelectorAll(".otp-input");
  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/\D/g, "");
      if (e.target.value && index < inputs.length - 1) inputs[index + 1].focus();
      const code = Array.from(inputs).map(i => i.value).join("");
      if (code.length === 6) verifyOTP();
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && index > 0) inputs[index - 1].focus();
    });
  });
}

export async function verifyOTP() {
  const inputs = document.querySelectorAll(".otp-input");
  const code = Array.from(inputs).map(i => i.value).join("");

  if (code.length !== 6) return showToast("Please enter the full 6-digit code.");
  if (!state.confirmationResult) return showToast("Session expired. Please try again.");

  try {
    await state.confirmationResult.confirm(code);
    closeLoginModal();
    showToast("Phone verified successfully!");
  } catch (error) {
    console.error(error);
    showToast("Invalid verification code.");
  }
}

export async function resendOTP() {
  const fullPhone = document.getElementById("otpPhoneDisplay").textContent;
  if (!fullPhone) return;

  try {
    if (window.recaptchaVerifier) {
      window.recaptchaVerifier.clear();
      window.recaptchaVerifier = null;
    }

    window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier("recaptcha-container", {
      size: "invisible"
    });

    state.confirmationResult = await auth.signInWithPhoneNumber(fullPhone, window.recaptchaVerifier);
    showToast("New code sent.");
  } catch (error) {
    console.error(error);
    showToast("Failed to resend code.");
  }
}

export function bindPhoneInputValidation() {
  const phoneInput = document.getElementById("loginPhone");
  const countrySelect = document.getElementById("phoneCountry");

  if (!phoneInput) return;

  phoneInput.addEventListener("input", () => {
    let value = phoneInput.value.replace(/\D/g, "");
    const countryCode = countrySelect?.value || "+63";

    if (countryCode === "+63") {
      value = value.slice(0, 11);
    } else {
      value = value.slice(0, 15);
    }

    phoneInput.value = value;
  });

  phoneInput.addEventListener("paste", (e) => {
    e.preventDefault();
    const pasted = (e.clipboardData || window.clipboardData).getData("text");
    let clean = pasted.replace(/\D/g, "");

    const countryCode = countrySelect?.value || "+63";
    if (countryCode === "+63") clean = clean.slice(0, 11);
    else clean = clean.slice(0, 15);

    phoneInput.value = clean;
  });
}

/* ==================== LOGIN MODAL */
export function openLoginModal() {
  resetLoginModal();
  const modal = document.getElementById("loginModalOverlay");
  if (modal) modal.classList.add("show");
  setTimeout(() => {
    const email = document.getElementById("loginEmail");
    if (email) email.focus();
  }, 150);
}

export function closeLoginModal() {
  const modal = document.getElementById("loginModalOverlay");
  if (modal) modal.classList.remove("show");
  resetLoginModal();
}

export function resetLoginModal() {
  const email = document.getElementById("loginEmail");
  const phone = document.getElementById("loginPhone");
  const errorEl = document.getElementById("loginError");
  const phoneErrorEl = document.getElementById("phoneLoginError");
  const emailForm = document.getElementById("emailLoginForm");
  const phoneForm = document.getElementById("phoneLoginForm");
  const authMainActions = document.getElementById("authMainActions");
  const otpSection = document.getElementById("otpSection");
  const modeLabel = document.getElementById("authModeLabel");
  const modeIcon = document.getElementById("authModeIcon");

  if (email) email.value = "";
  if (phone) phone.value = "";
  if (errorEl) {
    errorEl.textContent = "";
    errorEl.style.display = "none";
  }
  if (phoneErrorEl) {
    phoneErrorEl.textContent = "";
    phoneErrorEl.style.display = "none";
  }

  if (authMainActions) authMainActions.style.display = "flex";
  if (emailForm) emailForm.style.display = "flex";
  if (phoneForm) phoneForm.style.display = "none";
  if (otpSection) otpSection.style.display = "none";

  if (modeLabel) modeLabel.textContent = "Continue with Phone";
  if (modeIcon) modeIcon.innerHTML = '<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>';

  document.querySelectorAll(".otp-input").forEach(input => input.value = "");
  state.confirmationResult = null;
}

export function toggleAuthMode() {
  const emailForm = document.getElementById("emailLoginForm");
  const phoneForm = document.getElementById("phoneLoginForm");
  const modeLabel = document.getElementById("authModeLabel");
  const modeIcon = document.getElementById("authModeIcon");
  const loginError = document.getElementById("loginError");
  const phoneError = document.getElementById("phoneLoginError");

  if (!emailForm || !phoneForm || !modeLabel || !modeIcon) return;

  if (loginError) { loginError.style.display = "none"; loginError.textContent = ""; }
  if (phoneError) { phoneError.style.display = "none"; phoneError.textContent = ""; }

  const isEmailVisible = emailForm.style.display !== "none";

  if (isEmailVisible) {
    emailForm.style.display = "none";
    phoneForm.style.display = "flex";
    modeLabel.textContent = "Continue with Email";
    modeIcon.innerHTML = '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>';
    const phoneInput = document.getElementById("loginPhone");
    if (phoneInput) setTimeout(() => phoneInput.focus(), 100);
  } else {
    phoneForm.style.display = "none";
    emailForm.style.display = "flex";
    modeLabel.textContent = "Continue with Phone";
    modeIcon.innerHTML = '<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>';
    const emailInput = document.getElementById("loginEmail");
    if (emailInput) setTimeout(() => emailInput.focus(), 100);
  }
}

export function showLoginError(message) {
  const el = document.getElementById("loginError");
  if (!el) return;
  el.textContent = message;
  el.style.display = "block";
}

export function hideLoginError() {
  const el = document.getElementById("loginError");
  if (!el) return;
  el.textContent = "";
  el.style.display = "none";
}

/* ==================== LOGOUT */
export function performLogout() {
  showModal("Log Out?", "Are you sure you want to log out?", async () => {
    try {
      await auth.signOut();
      clearChat();
      showToast("Logged out successfully.");
    } catch (error) {
      console.error(error);
      showToast("Logout failed.");
    }
  });
}
