export const API_URL = "http://127.0.0.1:8001";

/* ==================== FIREBASE CONFIG */
export const firebaseConfig = {
  apiKey: "AIzaSyB_YeOzoMEvu5YO1Hbmp4tQz2Wg1R2ugF4",
  authDomain: "vista-845b5.firebaseapp.com",
  projectId: "vista-845b5",
  storageBucket: "vista-845b5.firebasestorage.app",
  messagingSenderId: "293786108305",
  appId: "1:293786108305:web:1cd222a0f2b3d3d2f7da30",
  measurementId: "G-W4LXTER3W1"
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
export const auth = firebase.auth();
