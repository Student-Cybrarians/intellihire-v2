'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { apiRequest } from '../../operational/frontend/apiClient';

type Score = { score: number; completed_at?: string | null } | null;
type AdminUser = {
  id: string;
  name?: string;
  email: string;
  role: string;
  status: string;
  overall?: number | null;
  last_login_at?: string | null;
  scores: Record<string, Score>;
};
type Activity = { event: string; created_at?: string | null; metadata?: Record<string, unknown> };
type Overview = {
  users: AdminUser[];
  activity: Activity[];
  stats: { users: number; active: number; admins: number; average_readiness?: number | null };
};

const modules = ['module1', 'module2', 'module3', 'module4', 'module5'];

export default function AdminPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load(search = '') {
    setLoading(true);
    setError('');
    try {
      const result = await apiRequest<Overview>(`/api/admin/overview${search ? `?q=${encodeURIComponent(search)}` : ''}`);
      setData(result);
    } catch (err: any) {
      if (err?.status === 401 || err?.status === 403) setError('Admin access is required for this page.');
      else setError(err?.message || 'Unable to load admin data.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  const users = useMemo(() => data?.users || [], [data]);

  return (
    <main className="m3" style={{ minHeight: '100vh' }}>
      <header>
        <Link href="/app/dashboard" className="brand" aria-label="Go to dashboard">✦ INTELLIHIRE</Link>
        <span>ADMIN CONSOLE</span>
        <nav aria-label="Admin navigation">
          <Link href="/app/dashboard">Dashboard</Link>
          <a href="/api/auth/logout">Sign out</a>
        </nav>
      </header>

      <section className="hero" style={{ minHeight: 220 }}>
        <div>
          <small>PLATFORM OPERATIONS</small>
          <h1>Admin intelligence.</h1>
          <p>Monitor users, module evidence and readiness from the same authenticated backend that powers IntelliHire.</p>
        </div>
        <div className="orb" aria-label="Average readiness">
          <small>AVG READINESS</small>
          <strong style={{ fontSize: 48 }}>{data?.stats.average_readiness ?? '—'}{data?.stats.average_readiness != null ? '%' : ''}</strong>
        </div>
      </section>

      {error ? <section className="card"><h2>Access / API error</h2><p>{error}</p><Link className="primary" href="/auth/google">Sign in with Google</Link></section> : null}

      {!error ? <>
        <section className="features" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {[
            ['USERS', data?.stats.users ?? '—'],
            ['ACTIVE', data?.stats.active ?? '—'],
            ['ADMINS', data?.stats.admins ?? '—'],
            ['AVG READINESS', data?.stats.average_readiness != null ? `${data.stats.average_readiness}%` : '—'],
          ].map(([label, value]) => <article className="card" key={label}><small>{label}</small><h2 style={{ fontSize: 32, marginBottom: 0 }}>{loading ? '…' : value}</h2></article>)}
        </section>

        <section className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <div><small>USER PERFORMANCE</small><h2>Connected evidence</h2></div>
            <form onSubmit={(e) => { e.preventDefault(); void load(query); }} style={{ display: 'flex', gap: 8 }}>
              <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search name or email" aria-label="Search users" style={{ minWidth: 220 }} />
              <button className="primary" type="submit">Search</button>
            </form>
          </div>
          <div style={{ overflowX: 'auto', marginTop: 18 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 900 }}>
              <thead><tr>{['User', 'Status', 'M1', 'M2', 'M3', 'M4', 'M5', 'Overall', 'Last login'].map((h) => <th key={h} style={{ textAlign: 'left', padding: 10, borderBottom: '1px solid rgba(145,167,197,.2)' }}>{h}</th>)}</tr></thead>
              <tbody>
                {users.map((user) => <tr key={user.id}>
                  <td style={{ padding: 10 }}><Link href={`/admin/users/${user.id}`} style={{ fontWeight: 800 }}>{user.name || 'Unnamed'}</Link><div style={{ color: '#91a7c5', fontSize: 12 }}>{user.email}</div></td>
                  <td style={{ padding: 10 }}>{user.status}</td>
                  {modules.map((m) => <td key={m} style={{ padding: 10 }}>{user.scores[m]?.score ?? '—'}</td>)}
                  <td style={{ padding: 10, fontWeight: 800 }}>{user.overall ?? '—'}</td>
                  <td style={{ padding: 10 }}>{user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : '—'}</td>
                </tr>)}
              </tbody>
            </table>
            {!loading && users.length === 0 ? <p style={{ color: '#91a7c5' }}>No users found.</p> : null}
          </div>
        </section>

        <section className="card">
          <small>RECENT AUDIT ACTIVITY</small>
          <h2>Operational events</h2>
          <div style={{ display: 'grid', gap: 8 }}>
            {(data?.activity || []).slice(0, 12).map((item, index) => <div key={`${item.event}-${item.created_at}-${index}`} style={{ display: 'flex', justifyContent: 'space-between', gap: 18, padding: '10px 0', borderBottom: '1px solid rgba(145,167,197,.12)' }}><strong>{item.event}</strong><span style={{ color: '#91a7c5' }}>{item.created_at ? new Date(item.created_at).toLocaleString() : '—'}</span></div>)}
          </div>
        </section>
      </> : null}
    </main>
  );
}
