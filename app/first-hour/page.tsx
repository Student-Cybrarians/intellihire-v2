'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import styles from './first-hour.module.css';
import MarketingShell from '../marketing/MarketingShell';

const steps = [
  { minute: '00', label: 'Start', title: 'Define your target role', text: 'Set the role you are preparing for and enter the job description or a short target brief.', action: 'Start with IntelliHire', href: '/api/auth/google' },
  { minute: '05', label: 'Profile', title: 'Build your evidence base', text: 'Bring in your resume so IntelliHire can extract skills, experience and evidence before scoring readiness.', action: 'Open Module 1', href: '/app/module1/overview' },
  { minute: '15', label: 'Practice', title: 'Run your first assessment', text: 'Use adaptive questions to expose strengths and priority gaps instead of relying on a single static score.', action: 'Explore Modules', href: '/features' },
  { minute: '30', label: 'Interview', title: 'Practice the hard conversation', text: 'Move from assessment evidence into technical and HR practice with role-aware prompts and feedback.', action: 'Explore Modules', href: '/features' },
  { minute: '45', label: 'Review', title: 'Turn feedback into actions', text: 'Review the evidence, identify the highest-impact gaps and choose the next preparation actions.', action: 'See platform', href: '/features' },
  { minute: '60', label: 'Ready', title: 'Leave with a preparation plan', text: 'Finish with a connected readiness view and a concrete roadmap for what to practice next.', action: 'Begin journey', href: '/api/auth/google' },
];

export default function FirstHourPage() {
  const [current, setCurrent] = useState(0);
  const [completed, setCompleted] = useState<number[]>([]);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('intellihire-first-hour') || '{}');
      if (Array.isArray(saved.completed)) setCompleted(saved.completed);
      if (typeof saved.current === 'number') setCurrent(Math.min(saved.current, steps.length - 1));
      if (typeof saved.startedAt === 'number') setStartedAt(saved.startedAt);
    } catch { /* ignore malformed local state */ }
  }, []);

  useEffect(() => {
    if (!startedAt) return;
    const timer = window.setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000);
    setElapsed(Math.floor((Date.now() - startedAt) / 1000));
    return () => window.clearInterval(timer);
  }, [startedAt]);

  useEffect(() => {
    localStorage.setItem('intellihire-first-hour', JSON.stringify({ current, completed, startedAt }));
  }, [current, completed, startedAt]);

  const progress = useMemo(() => Math.round((completed.length / steps.length) * 100), [completed]);
  const timeLabel = `${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;

  const begin = () => {
    if (!startedAt) setStartedAt(Date.now());
    setCurrent(0);
  };

  const completeCurrent = () => {
    if (!startedAt) setStartedAt(Date.now());
    setCompleted(prev => prev.includes(current) ? prev : [...prev, current].sort((a, b) => a - b));
    if (current < steps.length - 1) setCurrent(current + 1);
  };

  const reset = () => {
    setCurrent(0);
    setCompleted([]);
    setStartedAt(null);
    setElapsed(0);
    localStorage.removeItem('intellihire-first-hour');
  };

  return <MarketingShell active="features">
    <main className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroCopy}>
          <span className={styles.eyebrow}>THE INTELLIHIRE FIRST HOUR</span>
          <h1>From <em>“I need a job”</em> to “I know what to do next.”</h1>
          <p>A guided, minute-by-minute onboarding path inspired by the strongest idea in Munder Difflin's first-hour workflow: reduce the blank-page problem, make progress visible, and end the session with useful work already completed.</p>
          <div className={styles.actions}>
            <button className={styles.primary} type="button" onClick={begin}>{startedAt ? 'Resume first hour →' : 'Start first hour →'}</button>
            <Link className={styles.secondary} href="/features">Explore all modules</Link>
          </div>
          <p className={styles.note}>Your checklist progress is stored locally in this browser. Sign in to use the actual candidate modules.</p>
        </div>

        <div className={styles.commandCard} aria-label="First hour progress">
          <div className={styles.commandTop}><span>READINESS COMMAND CENTER</span><b>{startedAt ? '● ACTIVE' : '○ READY'}</b></div>
          <div className={styles.scoreRow}><div><small>SESSION TIME</small><strong>{timeLabel}</strong></div><div><small>PROGRESS</small><strong>{progress}%</strong></div></div>
          <div className={styles.progress}><span style={{ width: `${progress}%` }} /></div>
          <div className={styles.current}><small>NOW</small><h2>Minute {steps[current].minute} · {steps[current].label}</h2><p>{steps[current].title}</p></div>
        </div>
      </section>

      <section className={styles.timeline}>
        <div className={styles.sectionHead}><span>60 MINUTES · 6 MOVES</span><h2>One guided session. Real preparation at every stop.</h2><p>Each step points to an existing IntelliHire capability instead of creating a separate chatbot or disconnected workflow.</p></div>
        <div className={styles.stepList}>
          {steps.map((step, index) => <button key={step.minute} type="button" className={`${styles.step} ${index === current ? styles.active : ''} ${completed.includes(index) ? styles.done : ''}`} onClick={() => setCurrent(index)}>
            <span className={styles.minute}>{step.minute}</span><span className={styles.stepBody}><b>{step.label}</b><strong>{step.title}</strong><small>{step.text}</small></span><span className={styles.status}>{completed.includes(index) ? '✓' : index === current ? '→' : ''}</span>
          </button>)}
        </div>
      </section>

      <section className={styles.workspace}>
        <div className={styles.workspaceCopy}><span>YOUR CURRENT STOP</span><h2>Minute {steps[current].minute}: {steps[current].title}</h2><p>{steps[current].text}</p><div className={styles.workspaceActions}><Link className={styles.primary} href={steps[current].href}>{steps[current].action} →</Link><button className={styles.complete} type="button" onClick={completeCurrent}>{completed.includes(current) ? 'Completed ✓' : 'Mark complete'}</button></div></div>
        <div className={styles.evidence}><div><small>READINESS SIGNAL</small><strong>{Math.min(40 + completed.length * 10, 90)}%</strong></div><div><small>STEPS COMPLETE</small><strong>{completed.length}/{steps.length}</strong></div><div><small>NEXT</small><strong>{current < steps.length - 1 ? `Minute ${steps[current + 1].minute}` : 'Ready'}</strong></div></div>
      </section>

      <section className={styles.principles}>
        <div className={styles.sectionHead}><span>DESIGNED FOR INTELLIHIRE</span><h2>What we borrowed from the pattern — and what we changed.</h2></div>
        <div className={styles.cards}>
          <article><b>01 · Guided onboarding</b><h3>No empty dashboard</h3><p>The first session immediately gives a candidate a role, a resume, an assessment and a next action.</p></article>
          <article><b>02 · Visible state</b><h3>Progress you can see</h3><p>A timeline, active step, completion state and session clock make the preparation journey legible.</p></article>
          <article><b>03 · Human control</b><h3>AI assists; people decide</h3><p>Readiness evidence supports preparation. It does not make autonomous hiring or rejection decisions.</p></article>
        </div>
      </section>

      <section className={styles.finish}>
        <div><span>READY WHEN YOU ARE</span><h2>Finish the hour with a plan, not another score.</h2><p>Start with Module 1, work through the connected preparation flow, and return to this page whenever you want a guided next step.</p></div>
        <div className={styles.finishActions}><Link className={styles.primary} href="/app/module1/overview">Open Module 1 →</Link><button className={styles.secondaryButton} type="button" onClick={reset}>Reset first-hour progress</button></div>
      </section>
    </main>
  </MarketingShell>;
}
