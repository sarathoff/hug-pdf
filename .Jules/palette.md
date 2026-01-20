# Palette's Journal

## 2025-05-15 - TooltipProvider Requirement in Shadcn/UI
**Learning:** `shadcn/ui` Tooltip components require a wrapping `TooltipProvider` to function. It is not automatically included in the component library's `Tooltip` export.
**Action:** Always verify if `TooltipProvider` is present at the app root or page level when adding tooltips. If missing, wrap the relevant section.
