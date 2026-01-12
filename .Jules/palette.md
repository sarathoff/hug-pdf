## 2024-05-24 - Disabled Buttons and Tooltips
**Learning:** `shadcn/ui` buttons (and likely others) often use `pointer-events: none` when disabled. This prevents mouse events like hover from firing, meaning tooltips attached to disabled buttons won't show up. This is a common accessibility trap, as users often need to know *why* a button is disabled.
**Action:** Always wrap disabled buttons in a container (like a `<span>` or `<div>`) and attach the tooltip trigger to that container. Ensure the container is focusable if keyboard accessibility is required.

## 2024-05-24 - TooltipProvider Scope
**Learning:** `Tooltip` components in `shadcn/ui` require a `TooltipProvider` to be present in the component tree. If it's not at the root (`App.js`), it must be added to the specific page or component using tooltips.
**Action:** Check if `TooltipProvider` exists at the root. If not, wrap the local usage in `TooltipProvider` to ensure tooltips render.
