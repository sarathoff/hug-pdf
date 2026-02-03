## 2024-05-22 - Accessibility in Icon-Only Buttons
**Learning:** Icon-only buttons (like 'Send' or 'Back') are common in this design but often lack accessible labels, making them invisible to screen readers.
**Action:** Always verify `aria-label` is present when `children` contains only an icon component, or use `Tooltip` with proper trigger setup.
