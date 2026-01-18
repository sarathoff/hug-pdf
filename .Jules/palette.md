## 2026-01-18 - Tooltips and ARIA Labels
**Learning:** `shadcn/ui` Tooltip component requires a `TooltipProvider` to be present in the component tree. For standalone pages (like `EditorPage.jsx` which isn't wrapped in the main `Layout`), this provider must be added explicitly at the page level.
**Action:** Always verify if `TooltipProvider` is available in the context when adding Tooltips. If not, wrap the page or component tree with it.

**Learning:** Icon-only buttons using `shadcn/ui` Button component need `aria-label` for accessibility.
**Action:** Systematically audit icon-only buttons and add `aria-label` describing the action.
