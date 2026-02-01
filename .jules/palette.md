# Palette's UX/Accessibility Journal

## 2024-05-22 - Icon-Only Buttons and Toggle States
**Learning:** Icon-only buttons (like "Back", "Send", "Close") are common in this design system but often lack `aria-label`, making them inaccessible to screen readers. Also, custom button groups acting as mode toggles need `aria-pressed` to indicate the active state to assistive technology.
**Action:** When creating or modifying icon-only buttons, always add `aria-label`. For button groups that function as toggles, ensure the active button has `aria-pressed="true"` and others have `aria-pressed="false"`.
