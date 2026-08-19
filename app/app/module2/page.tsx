'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import AppShell from '../AppShell';

type Question = { id: string; prompt: string; options?: string[]; section?: string };
type Assessment = { id: string; status: string; ability: number; answered_ids: string[]; target_questions: number; section?: string };
type Event = { correct?: boolean; ability_after?: number; explanation?: string };
type Result = { score?: number; overall?: number; total?: number; correct?: number };

async function jsonFetch(path: string, options?: RequestInit) {
  const res = await fetch(path, { ...options, credentials: 'include', headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) } });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.error || 'Assessment request failed.');
  return data;
}

export default function Module2Page() {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [event, setEvent] = useState<Event | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function start() {
    setLoading(true); setError(''); setResult(null); setEvent(null); setSelected(null);
    try {
      const data = await jsonFetch('/api/module2/assessments', { method: 'POST', body: JSON.stringify({ target_questions: 8 }) });
      setAssessment(data);
      const next = await jsonFetch(`/api/module2/assessments/${data.id}/next`);
      setQuestion(next.question);
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to start assessment.'); }
    finally { setLoading(false); }
  }

  async function submit() {
    if (!assessment || !question || selected === null) return;
    setLoading(true); setError('');
    try {
      const data = await jsonFetch(`/api/module2/assessments/${assessment.id}/answer`, { method: 'POST', body: JSON.stringify({ question_id: question.id, answer: selected }) });
      setEvent(data.event); setAssessment(data.assessment); setResult(data.result); setSelected(null);
      if (data.assessment.status === 'ACTIVE') {
        const next = await jsonFetch(`/api/module2/assessments/${assessment.id}/next`);
        setQuestion(next.question);
      } else setQuestion(null);
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to submit answer.'); }
    finally { setLoading(false); }
  }

  async function abandon() {
    if (!assessment) return;
    setLoading(true); setError('');
    try { await jsonFetch(`/api/module2/assessments/${assessment.id}/abandon`, { method: 'POST' }); setAssessment(null); setQuestion(null); setEvent(null); setResult(null); setSelected(null); }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to abandon assessment.'); }
    finally { setLoading(false); }
  }

  useEffect(() => { jsonFetch('/api/module2/assessments/latest').then((d) => { const a = d.assessment; if (a?.status === 'ACTIVE') { setAssessment(a); return jsonFetch(`/api/module2/assessments/${a.id}/next`).then((n) => setQuestion(n.question)); } }).catch(() => undefined); }, []);

  return <AppShell><div className="card"><small>MODULE 2 · ADAPTIVE ASSESSMENT</small><h1>Adaptive Assessment</h1><p>Build measurable technical evidence through skill-based questions that adapt to candidate performance.</p>
    {error && <div className="notice" role="alert">{error}</div>}
    {!assessment && <div className="buttons"><button className="primary" onClick={start} disabled={loading}>{loading ? 'Starting…' : 'Start Assessment'}</button><Link className="secondary" href="/app/dashboard">Back to dashboard</Link></div>}
    {assessment && question && <section aria-live="polite"><p><strong>Progress:</strong> {assessment.answered_ids?.length || 0} / {assessment.target_questions}</p><h2>{question.prompt}</h2><div style={{ display: 'grid', gap: 10 }}>{(question.options || []).map((option, index) => <label key={index} style={{ padding: 12, border: '1px solid #ddd', borderRadius: 10, cursor: 'pointer' }}><input type="radio" name="answer" checked={selected === index} onChange={() => setSelected(index)} /> {option}</label>)}</div><div className="buttons" style={{ marginTop: 16 }}><button className="primary" onClick={submit} disabled={loading || selected === null}>{loading ? 'Submitting…' : 'Submit Answer'}</button><button className="secondary" onClick={abandon} disabled={loading}>Abandon</button></div>{event && <div className="notice" style={{ marginTop: 16 }}><strong>{event.correct ? 'Correct' : 'Review this answer'}</strong>{event.explanation && <p>{event.explanation}</p>}</div>}</section>}
    {assessment?.status === 'COMPLETED' && <section aria-live="polite"><h2>Assessment complete</h2><p>Your adaptive assessment has been scored.</p><div className="notice">Score: {result?.score ?? result?.overall ?? '—'}</div><div className="buttons"><button className="primary" onClick={start}>Start Another</button><Link className="secondary" href="/app/dashboard">Dashboard</Link></div></section>}
  </div></AppShell>;
}
