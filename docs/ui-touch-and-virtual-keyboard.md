# Touch & Virtual Keyboard

## Install
```bash
cd console
pnpm add simple-keyboard react-simple-keyboard
```

## Usage
- Add `TouchProvider` to `console/app/layout.tsx`.
- Ensure chat or form inputs expose `id="chat-input"` so the virtual keyboard can bind to them.

## Locales
- Built-in layouts for English and Persian (RTL). Toggle via the header button (EN/FA).
- Numbers pad available via the `{numbers}` key.

## Tips for iOS/Android
- Use `inputmode="numeric"` for numeric-only fields.
- Mitigate viewport jumps with CSS: `html, body { overscroll-behavior: contain; }`.

## Accessibility
- Buttons sized to at least 44x44 pixels.
- Respect `prefers-reduced-motion` if adding animations.
