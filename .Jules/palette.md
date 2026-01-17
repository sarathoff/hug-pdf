## 2026-01-17 - Async Loading States & Mobile A11y
**Learning:** Users on mobile rely heavily on icon-only buttons (like "Back" or "Refresh"), making `aria-label` critical for screen readers where context is limited. Also, in chat interfaces, the "Send" button must visually indicate loading to prevent double-submission and provide feedback, as the keyboard often remains open.
**Action:** Always wrap icon-only buttons with `aria-label` and implement visual loading states (spinner) inside the action button itself, not just disabling it.
