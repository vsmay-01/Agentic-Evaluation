React frontend for Agentic Evaluation

Run locally:

```powershell
cd frontend/react_app
npm install
npm start
```

The `package.json` contains a proxy to `http://localhost:8000` so the dev server forwards API calls to the backend.

Use the form in the app to submit a single prompt for evaluation to the backend endpoint `/evaluate/`.
