# Theming Strategy

- **Dark-first glass:** Background gradients originate from Tailwind utilities and `styles/globals.css`.
- **Theme provider:** `next-themes` toggles light/dark, persisted via `localStorage`.
- **RTL toggle:** Zustand store `useThemeStore` toggles `direction` stored in client state.
- **Typography:** Inter for latin, Vazirmatn for Persian with CSS variable fallback.
- **Accessibility:** Buttons use `focus-visible` outlines, color contrast meets WCAG AA (checked at 4.5:1).
