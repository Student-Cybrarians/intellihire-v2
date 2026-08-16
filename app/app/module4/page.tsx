import Link from 'next/link';
import AppShell from '../AppShell';

export default function Module4Page() {
  return <AppShell><div className="card"><small>MODULE 4 · HR & BEHAVIORAL</small><h1>HR & Behavioral Interview</h1><p>Practice structured behavioral answers with preparation focused on clarity, communication and confidence.</p><div className="notice">Module 4 workflow integration is the next implementation stage. Your dashboard navigation is active.</div><div className="buttons"><Link className="primary" href="/app/dashboard">Back to dashboard</Link></div></div></AppShell>;
}
