# OnlyStudies

Generate short, visual educational videos from a topic.

## Project layout

- `client/` — React browser app
- `server/` — FastAPI API and Manim renderer
- `specs/` — product specs and learning notes

## Start locally

Open two terminals from the project root. Do not move or copy a `.venv` directory: its executables contain absolute paths. Create it in `server/` instead.

**Terminal 1 — server**

```bash
cd server
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create `server/.env` from `server/.env.example` and set `GOOGLE_API_KEY` before generating a lesson. Confirm the server is ready at `http://localhost:8000/api/health`.

The default Gemini model is `gemini-2.5-flash`. If your API project does not have access to it, set `GEMINI_MODEL` in `server/.env` to an available text model. Failed render jobs retain their generated scene, so they can be corrected through the feedback box.

**Terminal 2 — client**

```bash
cd client
npm install
npm run dev
```

Wait for `npm install` to complete successfully before running Vite. Open the URL Vite prints, normally `http://localhost:5173`.
