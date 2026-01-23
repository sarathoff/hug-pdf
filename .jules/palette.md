## 2025-02-18 - Icon-Only Button Accessibility
**Learning:** The app uses many icon-only buttons (Back, Send, Close) in `EditorPage` without ARIA labels or tooltips, making them inaccessible to screen readers and unclear to users.
**Action:** Always add `aria-label` to icon-only buttons. Use `Tooltip` for desktop interfaces to provide context.
