# AI Decision Intelligence Platform (ADIP)

# Quick Start Guide

Version: v1.0.0

Edition: Research Edition

---

# Welcome

Welcome to the AI Decision Intelligence Platform (ADIP).

This guide helps you install and launch the platform for the first time.

Estimated setup time:

10–15 minutes

---

# Prerequisites

Install the following software before continuing.

• Git

• Python 3.11 or later

• Node.js 20 or later

• npm

• Modern web browser

---

# Step 1 — Clone the Repository

```bash
git clone https://github.com/ekjain27/ADIP.git

cd ADIP
```

---

# Step 2 — Create a Python Virtual Environment

Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

# Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# Step 4 — Install Frontend Dependencies

```bash
npm install
```

---

# Step 5 — Run the Frontend

```bash
npm run dev
```

The development server will display a URL similar to:

```
http://127.0.0.1:5173
```

Open this address in your browser.

---

# Step 6 — Verify Installation

Confirm that:

✓ Dashboard opens

✓ Navigation works

✓ Documentation is accessible

✓ No startup errors are displayed

---

# Run Tests

Execute:

```bash
pytest
```

Expected Release Result:

```
618 tests passed
```

---

# Build Release

```bash
npm run build
```

---

# Support

If the platform does not start correctly:

• Verify Python version

• Verify Node.js version

• Reinstall dependencies

• Review INSTALLATION.md

---

Congratulations!

ADIP is now ready for evaluation.
