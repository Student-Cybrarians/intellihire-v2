'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import styles from './marketing.module.css';

const stats = [
  ['5', 'Placement modules'],
  ['24/7', 'AI preparation'],
  ['3', 'Resume formats'],
  ['1', 'Career journey'],
];

const testimonials = [
  ['Aarav', 'Software Engineering Candidate', 'The resume-to-interview journey finally feels like one system instead of five disconnected tools.'],
  ['Meera', 'Final-year Student', 'The skill-gap view tells me what to learn next instead of only telling me what I did wrong.'],
  ['Rahul', 'Career Switcher', 'I can practice, review my performance and keep improving without losing my history.'],
];

const faqItems = [
  ['Is IntelliHire only for students?', 'No. It is designed for students, fresh graduates, career switchers and professionals preparing for a target role.'],
  ['Does AI decide whether I should be hired?', 'No. IntelliHire provides preparation and readiness evidence. Employment decisions remain human-controlled.'],
  ['Can I keep my previous results?', 'Yes. Authenticated candidate performance and assessment history are designed to persist in the platform database.'],
];

export default function MarketingShell({ children, active = '' }: { children: React.ReactNode; active?: string }) {
  const [menu, setMenu] = useState(false);
  const [dark, setDark] = useState(false);
  const [ready, setReady] = useState(false);
  const [slide, setSlide] = useState(0);
  const [faq, setFaq] = useState<number | null>(0);
  const [contact, setContact] = useState({ name: '', email: '', message: '' });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem('intellihire-theme');
    setDark(savedTheme === 'dark');
    const timer = window.setTimeout(() => setReady(true), 450);
    const onScroll = () => document.documentElement.style.setProperty('--scroll-y', `${window.scrollY * 0.08}px`);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => { window.clearTimeout(timer); window.removeEventListener('scroll', onScroll); };
  }, []);

  useEffect(() => { localStorage.setItem('intellihire-theme', dark ? 'dark' : 'light'); }, [dark]);

  const saveContactDraft = (e: React.FormEvent) => {
    e.preventDefault();
    if (!contact.name.trim() || !/^\S+@\S+\.\S+$/.test(contact.email) || contact.message.trim().length < 10) return;
    localStorage.setItem('intellihire-contact-draft', JSON.stringify({ ...contact, savedAt: new Date().toISOString() }));
    setSaved(true);
  };

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  return <div className={`${styles.site} ${dark ? styles.dark : ''}`}>
    {!ready && <div className={styles.preloader}><div className={styles.loaderMark}>IH</div><span>Preparing your career workspace…</span></div>}
    <header className={styles.navbar}>
      <Link className={styles.logo} href="/" onClick={() => setMenu(false)}><span>IH</span> INTELLIHIRE</Link>
      <button type="button" className={styles.mobileMenu} onClick={() => setMenu(!menu)} aria-label="Toggle navigation" aria-expanded={menu}>☰</button>
      <nav className={`${styles.navlinks} ${menu ? styles.open : ''}`} aria-label="Primary navigation">
        {['about','features','first-hour','courses','pricing','faq','contact'].map(item => <Link key={item} className={active === item ? styles.active : ''} onClick={() => setMenu(false)} href={`/${item}`}>{item === 'first-hour' ? 'First Hour' : item[0].toUpperCase()+item.slice(1)}</Link>)}
        <a className={styles.login} href="/api/auth/google" onClick={() => setMenu(false)}>Sign in</a>
        <button type="button" className={styles.theme} onClick={() => setDark(!dark)} aria-label={dark ? 'Switch to light theme' : 'Switch to dark theme'}>{dark ? '☀' : '☾'}</button>
      </nav>
    </header>

    <main>{children}</main>

    <section className={styles.statsBand} aria-label="IntelliHire statistics">
      {stats.map(([value, label]) => <div key={label}><strong>{value}</strong><span>{label}</span></div>)}
    </section>

    <section className={styles.testimonial}>
      <div className={styles.sectionHead}><span>REALISTIC, HUMAN-CENTRIC PRACTICE</span><h2>Built around the moments that matter.</h2></div>
      <div className={styles.quote}>
        <button type="button" onClick={() => setSlide((slide + testimonials.length - 1) % testimonials.length)} aria-label="Previous testimonial">←</button>
        <div><p>“{testimonials[slide][2]}”</p><strong>{testimonials[slide][0]}</strong><small>{testimonials[slide][1]}</small></div>
        <button type="button" onClick={() => setSlide((slide + 1) % testimonials.length)} aria-label="Next testimonial">→</button>
      </div>
    </section>

    <section className={styles.faqStrip}>
      <div className={styles.sectionHead}><span>FAQ</span><h2>Questions before you begin.</h2></div>
      <div className={styles.faqList}>{faqItems.map(([q,a], i) => <div className={styles.faqItem} key={q}><button type="button" onClick={() => setFaq(faq === i ? null : i)} aria-expanded={faq === i}>{q}<span>{faq === i ? '−' : '+'}</span></button>{faq === i && <p>{a}</p>}</div>)}</div>
    </section>

    <section className={styles.contactStrip} id="contact-form">
      <div><span>NEED HELP?</span><h2>Save a support request draft.</h2><p>This public form stores your request locally in this browser. For a request attached to your IntelliHire profile, sign in and use in-app support.</p></div>
      <form onSubmit={saveContactDraft}>
        <input required placeholder="Your name" value={contact.name} onChange={e => { setSaved(false); setContact({...contact,name:e.target.value}); }} />
        <input required type="email" placeholder="Email address" value={contact.email} onChange={e => { setSaved(false); setContact({...contact,email:e.target.value}); }} />
        <textarea required minLength={10} placeholder="What should we fix or build?" value={contact.message} onChange={e => { setSaved(false); setContact({...contact,message:e.target.value}); }} />
        <button className={styles.primary} type="submit">{saved ? 'Draft saved ✓' : 'Save request draft →'}</button>
      </form>
    </section>

    <footer className={styles.footer}><div><Link className={styles.logo} href="/"><span>IH</span> INTELLIHIRE</Link><p>Train Smarter. Interview Better. Get Hired.</p></div><div className={styles.footerLinks}><Link href="/about">About</Link><Link href="/features">Features</Link><Link href="/first-hour">First Hour</Link><Link href="/courses">Courses</Link><Link href="/pricing">Pricing</Link><Link href="/faq">FAQ</Link><Link href="/contact">Contact</Link></div><small>© 2026 IntelliHire. Career preparation, powered by AI.</small></footer>
    <button type="button" onClick={scrollToTop} className={styles.top} aria-label="Back to top">↑</button>
  </div>;
}
