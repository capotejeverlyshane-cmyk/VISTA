import { state } from './state.js';
import { showToast } from './utils.js';

/* ==================== VOICE INPUT */
export function initVoiceInput() {
  const voiceBtn = document.getElementById("voiceBtn");
  if (!voiceBtn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    voiceBtn.style.display = "none";
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "en-PH";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  state.recognition = recognition;

  voiceBtn.addEventListener("click", () => {
    if (state.isListening) {
      recognition.stop();
      return;
    }
    recognition.start();
  });

  recognition.onstart = () => {
    state.isListening = true;
    voiceBtn.classList.add("recording");
    voiceBtn.textContent = "⏺";
    showToast("Listening...");
  };

  recognition.onend = () => {
    state.isListening = false;
    voiceBtn.classList.remove("recording");
    voiceBtn.textContent = "🎤";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("user-input").value = transcript;
    showToast("Voice captured.");
  };

  recognition.onerror = () => {
    state.isListening = false;
    voiceBtn.classList.remove("recording");
    voiceBtn.textContent = "🎤";
    showToast("Voice input not available.");
  };
}

export function speakText(text) {
  if (!("speechSynthesis" in window)) {
    showToast("Text-to-speech is not supported on this device.");
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = mapSpeechLang(state.language);
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
}

function mapSpeechLang(lang) {
  if (lang === "tl") return "fil-PH";
  if (lang === "bis") return "en-PH";
  return "en-PH";
}
