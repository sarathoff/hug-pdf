## 2024-10-25 - Icon-only Button Accessibility
**Learning:** The application heavily relies on icon-only buttons (Send, Back, Mobile Menu) without `aria-label`s, making critical navigation and actions inaccessible to screen reader users. The "Send" button in the editor is particularly critical as it's the primary action.
**Action:** Always add `aria-label` to buttons that only contain an icon. For primary actions like "Send", consider adding a Tooltip as well to help all users understand the icon's function.
