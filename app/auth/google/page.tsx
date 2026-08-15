import Link from 'next/link';

export default function GoogleSignInPage() {
  return (
    <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24, background: '#071426', color: '#eef6ff', fontFamily: 'system-ui, sans-serif' }}>
      <section style={{ width: 'min(460px, 100%)', padding: 36, border: '1px solid #24405f', borderRadius: 24, background: '#0d1c33', textAlign: 'center' }}>
        <p style={{ color: '#68e7ff', letterSpacing: '.14em', fontSize: 12, fontWeight: 800 }}>INTELLIHIRE DEMO AUTH</p>
        <h1 style={{ fontSize: 38, margin: '12px 0' }}>Continue your journey</h1>
        <p style={{ color: '#b9c9db', lineHeight: 1.7 }}>
          Authentication is represented by a frontend service boundary in this build. No real Google credentials are collected here.
        </p>
        <Link href="/app/module3" style={{ display: 'inline-block', marginTop: 18, padding: '12px 18px', borderRadius: 10, background: '#35c8ff', color: '#04111e', fontWeight: 800, textDecoration: 'none' }}>
          Continue to technical interview
        </Link>
        <div><Link href="/" style={{ color: '#bfeaff', display: 'inline-block', marginTop: 18 }}>Back to IntelliHire</Link></div>
      </section>
    </main>
  );
}
