import { initializeApp } from "https://www.gstatic.com/firebasejs/12.5.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  OAuthProvider
} from "https://www.gstatic.com/firebasejs/12.5.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyAOrCsrWiQcywNe55_5BQXJo2PfpO6N2z8",
  authDomain: "efootballa-hub.firebaseapp.com",
  projectId: "efootballa-hub",
  storageBucket: "efootballa-hub.firebasestorage.app",
  messagingSenderId: "908928384482",
  appId: "1:908928384482:web:0332a48b1781da08850dbb",
  measurementId: "G-8TFLR27CYP"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export const appleProvider = new OAuthProvider("apple.com");
