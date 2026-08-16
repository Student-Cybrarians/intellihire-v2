import Link from 'next/link';
import AppShell from '../AppShell';

export default function Module5Page() {
  return <AppShell><div className="card"><small>MODULE 5 · HIRING READINESS</small><h1>Hiring Readiness</h1><p>Connect preparation evidence into readiness intelligence, skill gaps, recommendations and a career roadmap.</p><div className="notice">Module 5 workflow integration is the next implementation stage. Your dashboard navigation is active.</div><div className="buttons"><Link className="primary" href="/app/dashboard">Back to dashboard</Link></div></div></AppShell>;
}
