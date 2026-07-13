# RIVA Avatar Assets

- `riva-mascot.png` — Nova Tech's official full-body RIVA mascot artwork (white armour-inspired plating, dark navy visor, cyan glowing eyes, blue metallic joints, small magenta crown accent, shield emblem). Used on the startup screen.
- `riva-avatar-portrait.png` — a head-and-shoulders crop of the same artwork, sized for the compact circular avatar in `AvatarPanel.tsx`.

Both were sourced from Nova Tech's approved RIVA character design and resized/optimised for bundling with the desktop app (originals were ~1.2 MB each at 1024px+; these are downscaled and compressed for a reasonable install size).

## Swapping in a different or animated asset later

`AvatarPanel.tsx` reads the portrait as a static `<img>` inside `.avatar-stage`, with all state theming (color, glow, rotation speed) driven by CSS custom properties (`--avatar-accent`, `--avatar-accent-glow`) set per `avatar-state--*` class in `src/styles/app.css`. To upgrade later:

- **Animated WebP or video**: replace the `<img>` with a `<video autoPlay loop muted>` (or animated WebP `<img>`) using the same `.avatar-portrait` class.
- **Lottie JSON**: render with `lottie-react` inside `.avatar-stage`, keeping the existing glow/ring/wave elements around it.
- **GLB / 3D model**: render with `@react-three/fiber` inside `.avatar-stage`.

The six states (`idle`, `listening`, `thinking`, `speaking`, `error`, `offline`) are defined in the `AvatarState` type in `src/types/index.ts` and don't need to change for any of the above.
