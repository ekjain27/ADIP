# Deployment Guide

**Project:** AI Decision Intelligence Platform — Project-1  
**Version:** 1.0.0 Release Candidate

## Deployment Goal

Deploy only a verified release candidate after build, test, documentation, and production-cleanliness checks pass.

## Build

```bash
npm install
npm run build
```

The build command runs the TypeScript library build and Vite preview build according to `package.json`.

## Verification Before Deployment

```bash
npm test
pytest
```

Deployment should not proceed unless tests pass or verified exceptions are documented in the release audit.

## Release Artifacts

Expected release artifacts include:

- Source repository
- Production build output
- Release notes
- Changelog
- Documentation set
- Patent package summary
- Research package summary
- Release checklist

## Rollback

If deployment validation fails, restore the previous stable tagged version and investigate only verified failures.

## Production Cleanliness

Before release, verify:

- No unnecessary debug logs
- No duplicate generated artifacts committed unintentionally
- No dead code confirmed by audit
- No secrets committed
- `.gitignore` excludes generated folders
