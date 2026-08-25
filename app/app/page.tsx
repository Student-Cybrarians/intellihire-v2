'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import AppShell from './AppShell';
import { apiRequest } from '../../operational/frontend/apiClient';

type User = { name?: string; email?: string; role?: string };

export default function AppIndexPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await apiRequest<{ user?: User }>('/api/auth/me', { cache: 'no-store' });
        if (active) setUser(data?.user || null);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : 'Unable to verify your session.');
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  if (loading) return <main className="m3"><div className="empty"><h1>Preparing your workspace…</h1><p>Verifying your sign-in session.</p></div></main>;
  if (!user) return <main className="m3"><div className="empty"><h1>Sign in required</h1><p>{error || 'Sign in to access your IntelliHire workspace.'}</p><a className="primary" href="/api/auth/google">Continue with Google</a></div></main>;

  return <AppShell name={user.name}>
    <section className="hero" style={{ minHeight: 300 }}>
      <div>
        <small>CAREER INTELLIGENCE WORKSPACE</small>
        <h1>Welcome{user.name ? `, ${user.name.split(' ')[0]}` : ''}.</h1>
        <p>Choose the preparation stage you want to work on next.</p>
        <div className="buttons">
          <Link className="primary" href="/app/module1">Start with Resume Intelligence →</Link>
          <Link href="/app/module2">Open Adaptive Assessment</Link>
        </div>
      </div>
      <div className="orb" aria-label="IntelliHire workspace"><small>READINESS SIGNAL</small><strong style={{ fontSize: 58 }}>—</strong><span style={{ color: '#91a7c5', textAlign: 'center', maxWidth: 230 }}>Complete modules to build your evidence-based readiness profile.</span></div>
    </section>
    <section className="card"><small>YOUR FIVE-STAGE JOURNEY</small><h2>Choose where to prepare next</h2><div className="features" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
      {[['01','/app/module1','ATS & Resume Intelligence'],['02','/app/module2','Adaptive Assessment'],['03','/app/module3','Technical Interview'],['04','/app/module4','HR & Behavioral'],['05','/app/module5','Hiring Readiness']].map(([id, href, title]) => <Link href={href} key={id} className="card" style={{ margin: 0, textDecoration: 'none', color: 'inherit' }}><small>MODULE {id}</small><h3>{title}</h3><span style={{ color: '#70d9ff', fontWeight: 800 }}>Open module →</span></Link>)}
    </div></section>
  </AppShell>;
}
