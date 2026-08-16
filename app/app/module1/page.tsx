import Link from 'next/link';
import AppShell from '../AppShell';

export default function Module1Page() {
  return <AppShell><div className="card"><small>MODULE 1 · ATS & RESUME INTELLIGENCE</small><h1>Resume Intelligence</h1><p>Prepare to compare your resume against a target Job Description, identify missing skills and produce ATS-friendly evidence.</p><div className="notice">Module 1 workflow integration is the next implementation stage. Your dashboard navigation is active.</div><div className="buttons"><Link className="primary" href="/app/dashboard">Back to dashboard</Link></div></div></AppShell>;
}
