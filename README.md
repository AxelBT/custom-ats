## Web interface

A browser-based UI has been added on top of the existing CLI pipeline. It reuses
the same `evaluator.py` flow unchanged — the web layer only handles the file
upload and renders the result. The backend is a thin FastAPI wrapper around the
existing scoring function; the frontend is a single-page Vue app loaded from a
CDN, with no build step.

### Additional dependencies

```bash
$ pip install "fastapi>=0.138.0" "uvicorn[standard]" python-multipart
```

| Package              | Why                                                                       |
| -------------------- | ------------------------------------------------------------------------- |
| `fastapi>=0.138.0`   | `app.frontend()` (native static SPA serving) was introduced in 0.138.0.   |
| `uvicorn[standard]`  | ASGI server used to run the app.                                          |
| `python-multipart`   | Required by FastAPI to parse `multipart/form-data`, i.e. the PDF upload.  |

### New files

```text
.
├── main.py            # FastAPI app: /evaluate route + serves the frontend
└── static/
    ├── index.html     # Form view and result view, toggled by Vue
    ├── style.css
    └── index.js       # Vue app: upload, call /evaluate, render EvaluationData
```

### Running

```bash
$ uvicorn main:app --reload            # development, auto-reload
# or
$ uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000`. The same `DEVELOPMENT_MODE` and provider
settings from [Configuration](#configuration) still apply.

### Endpoint

`main.py` keeps the original evaluation function untouched — it still takes a
filesystem path — and exposes it over HTTP:

| Method | Path        | Body (`multipart/form-data`)   | Returns                      |
| ------ | ----------- | ------------------------------ | ---------------------------- |
| `POST` | `/evaluate` | `file` (PDF), `secteur` (opt.) | `{ "score": EvaluationData }`|

The route writes the uploaded PDF to a temporary file, passes its path to the
existing function (forwarding `secteur` as the optional `q` argument), deletes
the temp file, then returns the JSON result. Because the function is synchronous
and slow (PDF parsing plus LLM calls), the route is declared with `def` rather
than `async def`, so FastAPI runs it on its threadpool and the server stays
responsive.

The frontend unwraps the `score` key and renders `EvaluationData` as returned by
the agent: each category as `score / max` with a progress bar and its `evidence`,
the `bonus_points` and `deductions` totals with their `breakdown` / `reasons`,
and the `key_strengths` / `areas_for_improvement` lists. Field names are shown
raw, not relabeled.

### Notes

- The frontend and the API are served from the same origin, so there is no CORS
  configuration to manage.
- `app.frontend()` serves prebuilt static files only and does no server-side
  rendering; the Vue app's interactivity runs entirely in the browser.