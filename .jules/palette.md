## 2024-05-23 - Toggle Button State
**Learning:** Mode selectors implemented as buttons need `aria-pressed` to communicate active state to screen readers, as visual cues (colors) are insufficient for non-sighted users.
**Action:** Always add `aria-pressed={isActive}` to button-based toggle groups.
