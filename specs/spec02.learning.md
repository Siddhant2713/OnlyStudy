# Spec 02 learning notes

## Diagnosis

A Python virtual environment was moved from the repository root into `server/`. Virtual-environment scripts embed the directory that created them, so `pip` and `uvicorn` retained the old path and could not execute. The client installation was cancelled before Vite was downloaded, so `npm run dev` correctly reported that `vite` was missing.

## Changes made

1. Recreated `server/.venv` in its final location instead of moving it.
2. Made the server load `server/.env` regardless of the directory used to start Uvicorn.
3. Moved Vite, TypeScript, and type packages to `devDependencies`, pinned compatible major versions, and corrected the production build command.
4. Replaced the README with the exact, minimal commands required to start each application.

## Next learning plan

1. Let `python -m pip install -r requirements.txt` complete, then verify `/api/health`.
2. Let `npm install` complete, then run `npm run dev` and open the Vite URL.
3. Submit one low-quality silent lesson to verify API creation, status polling, rendering, and download end-to-end.
4. Add a persistent job store before deploying so a server restart does not lose lesson state.

## Verification update

The rebuilt environment started Uvicorn successfully and `GET /api/health` returned `{"status":"ok"}`. `npm install` completed and `npm run build` completed successfully with Vite.

## Revised next plan

1. Run `cd server && . .venv/bin/activate && uvicorn app.main:app --reload`.
2. In a second terminal run `cd client && npm run dev`.
3. Submit a low-quality silent lesson and use the resulting evidence to harden rendering failures before enabling voiceover.
