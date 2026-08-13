# IntelliHire — Module 1

Python/Flask recruitment screening application with a vanilla HTML/CSS/JavaScript frontend.

## Module 1 routes

- `/app/dashboard`
- `/app/module1/overview`
- `/app/module1/upload/resume`
- `/app/module1/upload/job-description`
- `/app/module1/analyzing`
- `/app/module1/results/ats-score`
- `/app/module1/results/matching`
- `/app/module1/results/skills`
- `/app/module1/results/keywords`
- `/app/module1/results/shortlist`
- `/app/module1/optimize/summary`
- `/app/module1/optimize/experience`
- `/app/module1/optimize/projects`
- `/app/module1/optimize/skills`
- `/app/module1/report`
- `/app/module1/history`

## ML

The demo uses real deterministic Python algorithms: tokenization, skill extraction, term-frequency vectors, cosine similarity, keyword coverage, and a centralized weighted ATS score. It is not a production AI model and shortlist decisions are explicitly simulated.

## Run

`pip install -r requirements.txt`

`python app.py`

Open `http://localhost:5000/app/module1/overview`.
