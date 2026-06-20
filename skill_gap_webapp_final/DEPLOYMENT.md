# Deploying Skill Gap Scanner — Render (backend) + Vercel (frontend)

This splits the app across two free hosts, which is the standard pattern for a Python backend + static frontend:

- **Backend (Flask + Gunicorn)** → [Render](https://render.com) — runs your actual ML/NLP code
- **Frontend (HTML/CSS/JS)** → [Vercel](https://vercel.com) — serves the static site, gives you a shareable link

## Prerequisites

You'll need a **GitHub repo** with this code pushed to it — both Render and Vercel deploy by connecting to a Git repository, not by uploading a zip.

```bash
cd skill-gap-webapp-deploy
git init
git add .
git commit -m "Initial commit: skill gap scanner"
```

Then create a new repo on [github.com/new](https://github.com/new), and push:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Step 1: Deploy the backend to Render

1. Go to [render.com](https://render.com) and sign up (no credit card needed for the free tier).
2. Click **New +** → **Web Service**.
3. Connect your GitHub account and select this repo.
4. Render should auto-detect the `render.yaml` file in the repo root and pre-fill the settings. If it doesn't, set these manually:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free
5. Click **Create Web Service**. The first build takes a few minutes (it's installing scikit-learn, NLTK, etc.).
6. Once live, you'll get a URL like `https://skill-gap-scanner-backend.onrender.com`. Test it:
   ```bash
   curl https://skill-gap-scanner-backend.onrender.com/health
   ```
   You should see `{"status": "ok"}`.

**About the free tier:** Render spins your service down after a period of inactivity. The first request after that takes 30-60 seconds while it wakes back up — this is normal, not a bug. The frontend already shows a "waking up the server" message after a few seconds of waiting, so it won't look broken.

## Step 2: Point the frontend at your live backend

Open `frontend/script.js` and change this line near the top:

```javascript
const API_BASE_URL = "http://127.0.0.1:5000";
```

to your actual Render URL:

```javascript
const API_BASE_URL = "https://skill-gap-scanner-backend.onrender.com";
```

Commit and push this change:

```bash
git add frontend/script.js
git commit -m "Point frontend at live Render backend"
git push
```

## Step 3: Deploy the frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up.
2. Click **Add New** → **Project**.
3. Import the same GitHub repo.
4. When configuring the project:
   - **Root Directory**: click "Edit" and set it to `frontend`
   - **Framework Preset**: "Other" (it's plain HTML/CSS/JS, no build step needed)
5. Click **Deploy**. This takes under a minute.
6. You'll get a live URL like `https://skill-gap-scanner.vercel.app` — this is your shareable link.

## Step 4: Lock down CORS (optional, but good practice)

Right now the backend accepts requests from any origin. Once you have your real Vercel URL, tighten this:

1. In the Render dashboard, go to your backend service → **Environment**.
2. Add an environment variable:
   - **Key**: `ALLOWED_ORIGINS`
   - **Value**: `https://skill-gap-scanner.vercel.app` (your actual Vercel URL — no trailing slash)
3. Save. Render will automatically redeploy with the restriction applied.

## Verifying everything works end to end

Visit your Vercel URL, upload a resume, paste a job description, and click "Scan for gaps." The very first request might take up to a minute (Render waking up) — after that, it should respond in a second or two.

## Troubleshooting

- **"Couldn't reach the analysis server"** → check that `API_BASE_URL` in `script.js` matches your actual Render URL exactly (https, no typos, no trailing slash), and that you redeployed the frontend after changing it.
- **CORS error in the browser console** → if you set `ALLOWED_ORIGINS`, double check it exactly matches your Vercel URL (including `https://`).
- **Backend build fails on Render** → check the build logs in the Render dashboard; this is almost always a `requirements.txt` issue, easy to spot from the log output.
- **First request always slow** → expected free-tier behavior, not a bug. Upgrading to Render's paid tier removes the spin-down.
