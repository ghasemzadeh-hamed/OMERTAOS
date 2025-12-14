# React 19.2.3 Upgrade

## Summary
- Updated all React consumers to use `react` and `react-dom` version `19.2.3`.
- Aligned TypeScript React type packages to `19.2.3` where applicable.
- Regenerated lockfiles via pnpm/npm and refreshed build/test tooling configs impacted by the React upgrade.

## Commands Run
- `cd console && pnpm install`
- `cd packages/ui-core && npm install --package-lock-only`
- `cd console && pnpm prisma:generate`
- `cd console && pnpm test`
- `cd console && pnpm build`

## Notes
- Added `eslint-plugin-react-hooks` to ensure linting dependencies resolve after the upgrade and removed a duplicate React hooks config extend.
- Generated a new `vitest.config.mts` to support ESM-friendly Vitest configuration.
- Prisma CLI scripts were approved during install to satisfy type generation required for builds.
