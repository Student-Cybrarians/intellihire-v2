import Link from 'next/link';
import MarketingShell from './marketing/MarketingShell';
import styles from './marketing/marketing.module.css';

const modules = [
  ['01','ATS & Resume Intelligence','Upload a resume, compare it with a target Job Description, find missing skills and create an ATS-friendly resume.'],
  ['02','Adaptive Assessment','Skill-based questions adapt to candidate performance and produce measurable assessment evidence.'],
  ['03','Technical Interview','Prepare with structured technical interview workflows, role-specific questions and performance feedback.'],
  ['04','HR & Behavioral','Practice behavioral interviews with AI-guided preparation for clarity, communication and confidence.'],
  ['05','Hiring Readiness','Combine Modules 1–4 into readiness intelligence, skill gaps, recommendations and a career roadmap.'],
];

export default function Home() {
  return <MarketingShell>
    <section className={styles.hero}>
      <div>
        <span className={styles.eyebrow}>AI-POWERED PLACEMENT & HIRING READINESS</span>
        <h1>Train smarter.<br/><em>Interview better.</em><br/>Get hired.</h1>
        <p>IntelliHire turns the hiring journey into one intelligent preparation system — ATS resume intelligence, adaptive assessments, technical interviews, HR practice and measurable career readiness.</p>
        <div className={styles.actions}>
          <Link className={styles.primary} href="/first-hour">Start your first hour →</Link>
          <a className={styles.secondary} href="/api/auth/google">Sign in</a>
          <Link className={styles.secondary} href="/features">Explore the platform</Link>
        </div>
        <p style={{fontSize:13}}>AI assists preparation and analysis. Employment decisions remain human-controlled.</p>
      </div>
      <div className={styles.heroCard} aria-label="Career readiness dashboard preview">
        <div className={styles.mockTop}><b>CAREER READINESS</b><span style={{color:'var(--cyan)'}}>● LIVE PROFILE</span></div>
        <div className={styles.mockScore}><small>OVERALL READINESS</small><strong>87%</strong><div>Strong foundation · 3 priority skill gaps</div></div>
        <div className={styles.mockGrid}>{modules.slice(0,4).map(x=><div className={styles.mockItem} key={x[0]}><b>Module {x[0]}</b><small>{x[1]}</small></div>)}</div>
      </div>
    </section>

    <section className={styles.section}>
      <div className={styles.sectionHead}><span>RESUME → ASSESSMENT → INTERVIEW → HR → READINESS</span><h2>Everything between “I applied” and “I’m ready.”</h2><p>Keep evidence, practice history, skill gaps and next actions connected to the role you actually want.</p></div>
      <div className={styles.cards}>
        {modules.slice(0,3).map(x=><article className={styles.feature} key={x[0]}><span className={styles.icon}>{x[0]}</span><h3>{x[1]}</h3><p>{x[2]}</p></article>)}
      </div>
    </section>

    <section className={styles.section}>
      <div className={styles.sectionHead}><span>FIVE CONNECTED MODULES</span><h2>One readiness signal. Five useful stages.</h2><p>Each module produces context for the next instead of becoming another disconnected score.</p></div>
      <div className={styles.cards}>
        {modules.slice(3).map(x=><article className={styles.feature} key={x[0]}><span className={styles.icon}>{x[0]}</span><h3>{x[1]}</h3><p>{x[2]}</p></article>)}
        <article className={styles.feature}><span className={styles.icon}>AI</span><h3>Real AI with guardrails</h3><p>OpenAI primary inference with NVIDIA fallback and deterministic cross-checks for grounded, timeout-safe preparation.</p></article>
      </div>
    </section>

    <section className={styles.section}>
      <div className={styles.sectionHead}><span>FOR ADMINISTRATORS</span><h2>See one candidate or compare an entire cohort.</h2><p>Admins can inspect user activity, compare Module 1–5 performance, manage support conversations and generate single or bulk Excel reports.</p></div>
      <div className={styles.cards}>
        <article className={styles.feature}><span className={styles.icon}>01</span><h3>Candidate performance</h3><p>Inspect module-level evidence and overall readiness for an individual candidate.</p></article>
        <article className={styles.feature}><span className={styles.icon}>02</span><h3>Cohort comparison</h3><p>Compare multiple candidates across modules and identify where preparation needs attention.</p></article>
        <article className={styles.feature}><span className={styles.icon}>03</span><h3>Reports & support</h3><p>Generate Excel reports and manage persistent User ↔ Admin questions, bugs and feature requests.</p></article>
      </div>
    </section>
  </MarketingShell>;
}
