# Skill Gap Scanner

An interactive web tool that compares a resume against a job description and tells you exactly what to fix.

**Input:** a resume (`.pdf` or `.docx`) + a job description (free text, pasted in)

**Output:**
- An **ATS match score** (0-100%) with a visual gauge — the percentage of job-description skills also found in the resume
- A three-column skill diff: found in resume / matched / missing for this role
- **Suggested fixes**: a concrete one-line suggestion for each missing skill
- If everything required is already present, the banner reads **"Skills are exactly matching."**

## How it works

```
Browser (HTML/CSS/JS)
    │  fetch() with FormData (file + text)
    ▼
Flask backend (app.py)
    │  1. Parse resume file → plain text       (document_parser.py)
    │  2. Extract skills from resume text       (nlp_preprocessing.py)
    │  3. Extract skills from JD text            (nlp_preprocessing.py)
    │  4. Compare the two skill sets
    │  5. Compute ATS score + fix suggestions    (ats_scoring.py)
    ▼
JSON response → rendered as a gauge + diff + fix list in the browser
```

Skill extraction uses taxonomy-based phrase matching against a 75-skill vocabulary across 9 categories. Since the job description is free text (not matched against a predefined role), "required skills" means **whatever skills are mentioned in the JD you paste in**.

### About the ATS score

The score is intentionally simple and transparent: `(matched skills / total JD skills) * 100`. This mirrors how the keyword-screening layer of most real-world ATS software actually works — it is not a simulation of any specific vendor's proprietary algorithm, just an honest reflection of keyword overlap.

## Project structure

```
.
├── render.yaml              <- Render deployment config (backend)
├── DEPLOYMENT.md            <- step-by-step Render + Vercel hosting guide
├── backend/
│   ├── app.py               <- Flask server + API endpoint
│   ├── ats_scoring.py        <- ATS score + fix suggestion logic
│   ├── document_parser.py    <- PDF/DOCX → text
│   ├── nlp_preprocessing.py   <- text → extracted skills
│   ├── skills_taxonomy.py     <- the 75-skill vocabulary
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── style.css
    ├── script.js
    └── vercel.json
```

## Running it locally

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open `frontend/index.html` in your browser (or serve it with `python -m http.server 8080` inside `frontend/` if your browser blocks local-file fetch requests).

## Deploying it live

See `DEPLOYMENT.md` for the full Render (backend) + Vercel (frontend) walkthrough.

## Limitations

- Skill extraction only recognizes skills in the predefined taxonomy — a skill phrased very differently from its canonical name (e.g. "LLMs" instead of "Hugging Face Transformers") won't be caught.
- Scanned/image-based PDFs with no selectable text won't extract anything.
- The ATS score reflects keyword overlap only, the same way most real ATS keyword-screening layers work — it does not assess resume formatting, layout parsability, or content quality beyond skill presence.
