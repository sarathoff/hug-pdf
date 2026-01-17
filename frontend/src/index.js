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
  if (
    args[0]?.message?.includes('signal is aborted') ||
    args[0]?.toString()?.includes('AbortError') ||
    args[0]?.name === 'AbortError'
  ) {
    return;
  }
  originalError.apply(console, args);
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <App />
);
