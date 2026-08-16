import Link from 'next/link';
import AppShell from '../AppShell';

export default function Module2Page() {
  return <AppShell><div className="card"><small>MODULE 2 · ADAPTIVE ASSESSMENT</small><h1>Adaptive Assessment</h1><p>Build measurable technical evidence through skill-based questions that adapt to candidate performance.</p><div className="notice">Module 2 workflow integration is the next implementation stage. Your dashboard navigation is active.</div><div className="buttons"><Link className="primary" href="/app/dashboard">Back to dashboard</Link></div></div></AppShell>;
}
