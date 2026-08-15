import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About IntelliHire — AI Career Intelligence Platform',
  description: 'Learn how IntelliHire connects AI-assisted placement preparation, career intelligence, and hiring readiness into one evidence-based workflow.',
  alternates: { canonical: 'https://intellihire-v2.vercel.app/about' },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return children;
}
