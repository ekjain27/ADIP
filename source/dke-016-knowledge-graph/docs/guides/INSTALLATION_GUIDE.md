# Installation Guide

**Project:** AI Decision Intelligence Platform — Project-1  
**Version:** 1.0.0 Release Candidate

## Requirements

- Node.js 20 or newer
- npm
- Python 3.11 or newer
- pip
- Git

## Install Frontend / TypeScript Dependencies

```bash
npm install
```

## Install Python Test Dependencies

Use a virtual environment if needed:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

Install the Python dependencies required by the test environment. If a requirements file is added later, use it as the source of truth.

## Verify Installation

```bash
npm run build
npm test
pytest
```

## Notes

- `node_modules/`, `dist/`, and `preview-dist/` are generated artifacts and are ignored by `.gitignore`.
- Final dependency and command verification must be completed during the release audit.
