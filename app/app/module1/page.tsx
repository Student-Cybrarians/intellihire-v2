'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';
import AppShell from '../AppShell';

type Result = {
  atsScore?: number;
  overallMatch?: number;
  skillsMatch?: number;
  keywordMatch?: number;
  semanticSimilarity?: number;
  missingSkills?: string[];
  shortlist?: string;
  isSimulated?: boolean;
};

export default function Module1Page() {
  const [resume, setResume] = useState('');
  const [job, setJob] = useState('');
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function analyze(event: FormEvent) {
    event.preventDefault();
    setError('');
    setResult(null);
    if (resume.trim().length < 40 || job.trim().length < 40) {
      setError('Please provide a meaningful resume and job description before analyzing.');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          resume: { text: resume },
          job: { text: job },
        }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) throw new Error(data?.error || 'Analysis could not be completed.');
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis could not be completed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="card">
        <small>MODULE 1 · ATS & RESUME INTELLIGENCE</small>
        <h1>Resume Intelligence</h1>
        <p>Compare your resume against a target Job Description, identify skill gaps, and improve ATS alignment using evidence from the supplied text.</p>

        <form onSubmit={analyze} style={{ display: 'grid', gap: 16, marginTop: 24 }}>
          <label>
            <strong>Resume</strong>
            <textarea aria-label="Resume" value={resume} onChange={(e) => setResume(e.target.value)} placeholder="Paste your resume text here…" rows={12} style={{ width: '100%', marginTop: 8, padding: 12, borderRadius: 12, boxSizing: 'border-box' }} />
          </label>
          <label>
            <strong>Job Description</strong>
            <textarea aria-label="Job Description" value={job} onChange={(e) => setJob(e.target.value)} placeholder="Paste the target job description here…" rows={12} style={{ width: '100%', marginTop: 8, padding: 12, borderRadius: 12, boxSizing: 'border-box' }} />
          </label>
          {error && <div className="notice" role="alert">{error}</div>}
          <div className="buttons">
            <button className="primary" type="submit" disabled={loading}>
              {loading ? 'Analyzing…' : 'Analyze Resume'}
            </button>
            <Link className="secondary" href="/app/dashboard">Back to dashboard</Link>
          </div>
        </form>

        {result && (
          <section aria-live="polite" style={{ marginTop: 28 }}>
            <h2>ATS Analysis</h2>
            <div className="cards">
              <div className="card"><strong>ATS score</strong><h2>{result.atsScore ?? '—'}%</h2></div>
              <div className="card"><strong>Overall match</strong><h2>{result.overallMatch ?? '—'}%</h2></div>
              <div className="card"><strong>Skills match</strong><h2>{result.skillsMatch ?? '—'}%</h2></div>
              <div className="card"><strong>Keywords</strong><h2>{result.keywordMatch ?? '—'}%</h2></div>
            </div>
            <p><strong>Recommendation:</strong> {result.shortlist || 'Review the analysis and improve the identified gaps.'}</p>
            {!!result.missingSkills?.length && (
              <div className="notice"><strong>Skills to strengthen:</strong> {result.missingSkills.join(', ')}</div>
            )}
            {result.isSimulated && <div className="notice">This result is marked simulated by the backend. Treat it as an analysis aid, not a hiring decision.</div>}
          </section>
        )}
      </div>
    </AppShell>
  );
}
