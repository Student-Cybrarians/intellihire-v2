# IntelliHire v2 🚀

AI-Powered Hiring Platform with 5 comprehensive interview preparation modules.

## Live Site
**https://student-cybrarians.github.io/intellihire-v2/**

## Modules

### Module 01 — ATS Resume Analyzer
Upload resume → Get ATS score → Keyword analysis → Download optimized PDF

### Module 02 — Aptitude Round  
Adaptive MCQ test with difficulty adjustment, voice mode, performance charts

### Module 03 — Technical Round
Live code editor with Monaco, AI code review, problem generation

### Module 04 — HR Simulator
Voice-enabled HR interview, STAR method analysis, filler word detection

### Module 05 — Behavioral Analysis
Webcam recording, real-time transcript, behavioral scoring with radar charts

## Tech Stack
- **Frontend**: Pure HTML/CSS/JavaScript
- **AI**: OpenAI GPT-4o API
- **Deployment**: GitHub Pages + GitHub Actions
- **Libraries**: Chart.js, jsPDF, Monaco Editor

## Architecture
- Client-side only (no backend server)
- API key injected at build time via GitHub Actions
- Direct browser → OpenAI API communication
- Auto-deploys on push to main branch

## Setup

1. **Add API Key as GitHub Secret**:
   - Go to Repository Settings → Secrets and variables → Actions
   - Add new secret: `OPENAI_API_KEY` with your key

2. **Enable GitHub Pages**:
   - Settings → Pages
   - Source: Deploy from branch
   - Branch: `gh-pages` / `root`

3. **Push to deploy**:
   ```bash
   git push origin main
   ```

GitHub Actions will automatically inject the API key and deploy to Pages.

## Local Development

Replace the placeholder in `config.js`:
```javascript
const OPENAI_API_KEY = 'your-api-key-here';
```

Then open `index.html` in a browser.

## Built By
**Student-Cybrarians** — B.Tech CSE (AI/ML) Major Project

---

© 2025 IntelliHire · Powered by OpenAI GPT-4o API
