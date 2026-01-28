## 2025-02-21 - Editor Accessibility
**Learning:** `EditorPage` buttons (Back, Send, Mode) lacked accessible labels and tooltips, making navigation difficult for screen readers and unclear for mouse users. `TooltipProvider` must wrap the page content for `Tooltip` components to work.
**Action:** Always wrap interactive pages in `TooltipProvider` and verify `aria-label` on icon-only buttons.

## 2025-02-21 - Build Tooling Incompatibility
**Learning:** `react-scripts` v5 fails with ESLint 9 due to removed options (`extensions`, `resolvePluginsRelativeTo`).
**Action:** Use `DISABLE_ESLINT_PLUGIN=true` when running build or start commands in this specific repo environment until tooling is upgraded.
