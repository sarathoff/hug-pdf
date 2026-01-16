## 2026-01-16 - TooltipProvider Scope
**Learning:** `shadcn/ui` Tooltips require a `TooltipProvider`. In this project, it's not wrapped globally in `App.js` or `Layout.jsx`, so it must be added to individual pages (e.g., `EditorPage.jsx`) to function.
**Action:** Always check for `TooltipProvider` when adding Tooltips. If missing, wrap the page or component tree.
