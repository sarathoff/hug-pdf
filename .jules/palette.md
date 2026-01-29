## 2026-01-29 - Tooltips on Disabled Buttons
**Learning:** shadcn/ui buttons apply `pointer-events-none` when disabled, which prevents tooltips from triggering on hover or focus. This creates an accessibility gap where users cannot learn why an action is unavailable.
**Action:** Wrap disabled buttons in a container (like a `<span>`) that serves as the tooltip trigger. Ensure the container is interactive (`tabIndex="0"`) if keyboard access to the disabled state explanation is needed, or just handles hover events.
