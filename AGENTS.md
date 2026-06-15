# AGENTS.md

## Cursor Cloud specific instructions

This repository is a single-page static web app: the entire UI and its interactive
JavaScript live in `index.html`. There is no package manager, build step, lint, or
automated test suite.

### Running the app (development)

Serve the static files with Python's built-in server (Python 3 is pre-installed):

```bash
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000/`. Run it from the repo root so `index.html` is served
at `/`.

Notes:
- This is a static server with no hot reload — refresh the browser after editing
  `index.html` to see changes.
- The app's core functionality is entirely client-side (see the `<script>` block in
  `index.html`): the "Scenarios" buttons (e.g. "Simulate Sensor Malfunction") drive
  alerts, KPIs, the event log, and the chart. A good smoke test is to load the page,
  click "Simulate Sensor Malfunction", then click "Dispatch Repair Crew" and confirm the
  dashboard transitions into and out of the malfunction state.

### Build / deploy

There is no local build. Production deploy is handled by GitHub Pages via
`.github/workflows/static.yml`, which uploads the repository contents as-is on pushes to
`main`.

### Lint / test

There is no lint or test tooling configured in this repository.
