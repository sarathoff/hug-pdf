## 2024-05-22 - Visual Toggles vs Accessible Toggles
**Learning:** Visual toggle buttons (using color to indicate state) are often implemented as standard buttons without semantic state information.
**Action:** Always add `aria-pressed` or `aria-selected` to buttons that function as toggles or tabs to ensure screen readers announce the active state, not just the label.

## 2024-05-22 - Icon-Only Buttons
**Learning:** Icon-only buttons are frequent accessibility failures in rapid development. Even with tooltips, they often lack accessible names for screen readers.
**Action:** Systematically audit all `size="icon"` or empty-text buttons and ensure they have a distinct `aria-label`.
