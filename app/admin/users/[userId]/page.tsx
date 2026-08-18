'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiRequest } from '../../../../operational/frontend/apiClient';

type Detail = {
  user: { name?: string; email: string; role: string; status: string; overall?: number | null };
  performance: Record<string, { score: number; completed_at?: string | null } | null>;
  activity: { event: string; created_at?: string | null; metadata?: Record<string, unknown> }[];
};

export default function AdminUserPage() {
  const params = useParams<{ userId: string }>();
  const [data, setData] = useState<Detail | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!params?.userId) return;
    apiRequest<Detail>(`/api/admin/users/${encodeURIComponent(params.userId)}`)
      .then(setData)
      .catch((err: any) => setError(err?.message || 'Unable to load user.'));
  }, [params?.userId]);

  if (error) return <main className="m3"><section className="card"><h1>Unable to load user</h1><p>{error}</p><Link className="primary" href="/admin">Back to admin</Link></section></main>;
  if (!data) return <main className="m3"><section className="card"><h1>Loading…</h1></section></main>;

  return <main className="m3">
    <header><Link href="/admin" className="brand">✦ INTELLIHIRE</Link><span>ADMIN · USER DETAIL</span><nav><Link href="/admin">All users</Link><a href="/api/auth/logout">Sign out</a></nav></header>
    <section className="hero" style={{ minHeight: 210 }}><div><small>CANDIDATE PROFILE</small><h1>{data.user.name || data.user.email}</h1><p>{data.user.email} · {data.user.role} · {data.user.status}</p></div><div className="orb"><small>OVERALL</small><strong style={{ fontSize: 48 }}>{data.user.overall ?? '—'}{data.user.overall != null ? '%' : ''}</strong></div></section>
    <section className="features" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>{['module1','module2','module3','module4','module5'].map((m) => <article className="card" key={m}><small>{m.toUpperCase()}</small><h2>{data.performance[m]?.score ?? '—'}</h2><p>{data.performance[m]?.completed_at ? new Date(data.performance[m]!.completed_at!).toLocaleDateString() : 'Not completed'}</p></article>)}</section>
    <section className="card"><small>AUDIT TRAIL</small><h2>Recent activity</h2>{data.activity.map((item, i) => <div key={`${item.event}-${i}`} style={{ padding: 10, borderBottom: '1px solid rgba(145,167,197,.12)', display: 'flex', justifyContent: 'space-between', gap: 18 }}><strong>{item.event}</strong><span style={{ color: '#91a7c5' }}>{item.created_at ? new Date(item.created_at).toLocaleString() : '—'}</span></div>)}</section>
  </main>;
}
