## 2024-10-24 - Tooltips on Disabled Buttons
**Learning:** The `shadcn/ui` Button component applies `pointer-events-none` in its disabled state. To enable tooltips on disabled buttons, the button must be wrapped in an interactive container (e.g., a `<span>` with `inline-flex` to maintain layout) that acts as the `TooltipTrigger`.
**Action:** When implementing tooltips for disabled actions, wrap the `Button` in a `<span>` and place the `TooltipTrigger` on the span.
