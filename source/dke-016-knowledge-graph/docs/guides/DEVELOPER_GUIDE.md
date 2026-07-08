# Developer Guide

## Development Policy

Project-1 follows a frozen-module policy. Developers must not redesign completed modules during release hardening.

## Allowed During Release Hardening

- Verified bug fixes
- Documentation alignment
- Production cleanup
- Test/build fixes
- Dead-code removal only after verification

## Not Allowed During Release Hardening

- New modules
- New architecture mechanisms
- Roadmap changes
- Backend redesign
- Frontend architecture redesign
- Enterprise data onboarding

## Commands

```bash
npm install
npm run build
npm test
pytest
```

## Repository Areas

- `src/dke/`: backend decision intelligence modules
- `src/ux/`: frontend UX implementation
- `tests/`: Python regression tests
- `docs/`: release and UX documentation
- `dist/`, `preview-dist/`: generated build artifacts
