## 2025-05-23 - Interactive Button Accessibility
**Learning:** Icon-only buttons often lack accessible labels, and primary action buttons (like Send) miss visual loading states, creating confusion for screen readers and users on slow connections.
**Action:** Always add `aria-label` to icon-only buttons and replace action icons with spinners (e.g., `Loader2`) during loading states.
