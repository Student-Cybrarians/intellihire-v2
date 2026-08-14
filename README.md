# IntelliHire

IntelliHire is an AI-based placement and career-intelligence platform built around resume intelligence, adaptive assessment, technical interview practice, HR interview coaching, and candidate readiness.

## Current live architecture

- Flask application with authenticated USER / ADMIN flows
- Google OAuth session authentication
- Module 1 real server-side AI inference through configured OpenAI-compatible and NVIDIA providers
- Module 1 timeout budget with provider fallback and deterministic ATS fallback
- PDF / DOCX / TXT / Markdown resume extraction
- Evidence-based ATS cross-check using skill matching, TF-IDF semantic similarity, lexical matching, and BM25
- Skill alias normalization and career-gap analysis
- Career Intelligence API for personalized context, skill gaps, and preparation plans
- DOCX / PDF / CSV resume export
- PostgreSQL-backed performance tracking where configured
- GitHub Actions regression tests

## AI provider environment

Configure secrets server-side only. Never expose provider keys to the browser.

```text
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1/chat/completions
OPENAI_MODEL=gpt-5-mini
NVIDIA_API_KEY=
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
NVIDIA_MODEL=nvidia/nemotron-3-nano-30b-a3b-reasoning
MODULE1_AI_PROVIDER_TIMEOUT_SECONDS=10
MODULE1_AI_TOTAL_TIMEOUT_SECONDS=22
```

## Run

```bash
pip install -r requirements.txt
python app.py
```

Production uses the configured Gunicorn/Vercel deployment path.

## Module 1

Open `/app/module1/overview` after authentication.

The production flow is:

```text
Resume upload
  -> document extraction
  -> deterministic ATS baseline
  -> real AI provider
  -> evidence cross-check
  -> skill gaps
  -> preparation plan
  -> ATS-friendly resume
  -> DOCX / PDF / CSV
```

If the AI provider is unavailable, IntelliHire explicitly reports deterministic fallback mode rather than fabricating an AI result.

## Career Intelligence API

Authenticated users can POST to `/auth/career/intelligence` with a target role and profile. The service returns structured career context, required/matched/missing skills, and an evidence-oriented preparation plan.

The career intelligence layer is for candidate preparation and discovery. It must not be used as an autonomous hiring or rejection decision system.

## Testing

GitHub Actions runs Python compilation plus Module 1 / Module 4 regression tests. The test suite includes provider fallback, timeout handling, skill normalization, ATS ML matching, BM25, and career-gap planning.
