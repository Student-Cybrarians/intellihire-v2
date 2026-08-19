'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import AppShell from '../AppShell';
import { apiRequest } from '../../../operational/frontend/apiClient';

const modules = [
  { id: '01', href: '/app/module1', title: 'ATS & Resume Intelligence', text: 'Match your resume to a target role, identify gaps and prepare ATS-ready evidence.' },
  { id: '02', href: '/app/module2', title: 'Adaptive Assessment', text: 'Build measurable technical evidence through skill-based adaptive questions.' },
  { id: '03', href: '/app/module3', title: 'Technical Interview', text: 'Practice structured technical interviews with persistent progress and evaluation.' },
  { id: '04', href: '/app/module4', title: 'HR & Behavioral', text: 'Strengthen communication, behavioral answers and interview confidence.' },
  { id: '05', href: '/app/module5', title: 'Hiring Readiness', text: 'Combine preparation evidence into readiness intelligence and next actions.' },
];

type User = { name?: string; email?: string; role?: string };

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [unauthorized, setUnauthorized] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    const loadSession = async () => {
      try {
        let data;
        try {
          data = await apiRequest<{ authenticated?: boolean; user?: User }>('/api/auth/me', { cache: 'no-store' });
        } catch (firstError) {
          const status = typeof firstError === 'object' && firstError && 'status' in firstError
            ? Number((firstError as { status?: number }).status)
            : 0;
          if (![401, 403, 404, 405, 500].includes(status)) throw firstError;
          data = await apiRequest<{ authenticated?: boolean; user?: User }>('/auth/me', { cache: 'no-store' });
        }
        if (!active) return;
        if (!data?.user) {
          setUnauthorized(true);
          return;
        }
        setUser(data.user);
      } catch (err) {
        if (!active) return;
        const status = typeof err === 'object' && err && 'status' in err ? Number((err as { status?: number }).status) : 0;
        if (status === 401 || status === 403) setUnauthorized(true);
        else setError('We could not verify your session. Please try signing in again.');
      } finally {
        if (active) setLoading(false);
      }
    };
    loadSession();
    return () => { active = false; };
  }, []);

  if (unauthorized) {
    return <main className="m3"><div className="empty"><h1>Session required</h1><p>Your sign-in session is missing or has expired. Continue with Google to return to your dashboard.</p><a className="primary" href="/api/auth/google">Continue with Google</a></div></main>;
  }

  if (error) {
    return <main className="m3"><div className="empty"><h1>Dashboard connection error</h1><p>{error}</p><div className="buttons"><button className="primary" onClick={() => window.location.reload()}>Retry</button><a className="secondary" href="/api/auth/google">Sign in again</a></div></div></main>;
  }

  return <AppShell name={user?.name}>
    <section className="hero" style={{ minHeight: 300 }}>
      <div>
        <small>CAREER INTELLIGENCE WORKSPACE</small>
        <h1>{loading ? 'Preparing your workspace…' : `Welcome${user?.name ? `, ${user.name.split(' ')[0]}` : ''}.`}</h1>
        <p>One connected preparation journey from resume evidence to hiring readiness.</p>
        <div className="buttons">
          <Link className="primary" href="/app/module3/setup">Start Technical Interview →</Link>
          <Link href="/app/module1">Open Resume Intelligence</Link>
        </div>
      </div>
      <div className="orb" aria-label="IntelliHire readiness workspace">
        <small>READINESS SIGNAL</small>
        <strong style={{ fontSize: 58 }}>—</strong>
        <span style={{ color: '#91a7c5', textAlign: 'center', maxWidth: 230 }}>Complete modules to build your evidence-based readiness profile.</span>
      </div>
    </section>

    <section className="card">
      <small>YOUR FIVE-STAGE JOURNEY</small>
      <h2>Choose where to prepare next</h2>
      <div className="features" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
        {modules.map((module) => <Link href={module.href} key={module.id} className="card" style={{ margin: 0, textDecoration: 'none', color: 'inherit' }}>
          <small>MODULE {module.id}</small>
          <h3>{module.title}</h3>
          <p>{module.text}</p>
          <span style={{ color: '#70d9ff', fontWeight: 800 }}>Open module →</span>
        </Link>)}
      </div>
    </section>

    <section className="grid2">
      <article className="card"><small>CONNECTED EVIDENCE</small><h2>Build context, not isolated scores.</h2><p>Each module is designed to contribute useful context to the next stage. Scores are evidence for preparation, not automated employment decisions.</p></article>
      <article className="card"><small>AI GUARDRAIL</small><h2>Human-controlled outcomes.</h2><p>AI can assist preparation, feedback and analysis. Employment decisions remain outside the automated system.</p></article>
    </section>
  </AppShell>;
}
