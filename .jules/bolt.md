# Bolt's Journal

## 2024-05-22 - [Initial Entry]
**Learning:** Initialized Bolt's journal.
**Action:** Record critical performance learnings here.

## 2024-05-22 - [AuthContext Reference Instability]
**Learning:** `AuthContext` methods (like `refreshUser`) were recreated on every render because they weren't wrapped in `useCallback`. This caused `useEffect` hooks in consumers (like `EditorPage.jsx`) to re-fire unnecessarily, creating potential infinite loops where an effect calls a function -> function updates state -> context re-renders -> function recreated -> effect runs again.
**Action:** Always wrap context value and functions in `useMemo`/`useCallback` to ensure referential stability, especially when those functions are used in `useEffect` dependency arrays downstream.
