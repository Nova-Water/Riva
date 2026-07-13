# RIVA Avatar Assets

This folder is where a final RIVA avatar asset can be dropped in to replace
the current animated CSS placeholder in `src/components/AvatarPanel.tsx`.

Supported formats the component is designed to accept later:

- Static image: PNG / WebP (swap the `.avatar-core` background for an `<img>`)
- Animated WebP or video (`<video autoPlay loop muted>` in place of `.avatar-core`)
- Lottie JSON (render with `lottie-react` inside `.avatar-stage`)
- GLB / 3D model (render with `@react-three/fiber` inside `.avatar-stage`)

The component already exposes six states you can hook into the new asset:
`idle`, `listening`, `thinking`, `speaking`, `error`, `offline` (see the
`AvatarState` type in `src/types/index.ts`).
