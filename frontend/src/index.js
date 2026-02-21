import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress AbortError spam at the window level
// These are caused by Supabase realtime cleanup and are harmless
window.addEventListener('error', (event) => {
  if (
    event.message?.includes('signal is aborted') ||
    event.error?.name === 'AbortError' ||
    event.error?.message?.includes('signal is aborted')
  ) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
});

window.addEventListener('unhandledrejection', (event) => {
  if (
    event.reason?.name === 'AbortError' ||
    event.reason?.message?.includes('signal is aborted')
  ) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
});

// Also suppress in console
const originalError = console.error;
console.error = (...args) => {
  const errorString = args.map(arg => arg?.toString() || '').join(' ');
  if (
    errorString.includes('signal is aborted') ||
    errorString.includes('AbortError') ||
    args.some(arg => arg?.name === 'AbortError' || arg?.code === 20)
  ) {
    return;
  }
  originalError.apply(console, args);
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <App />
);
