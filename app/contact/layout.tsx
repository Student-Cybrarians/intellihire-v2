import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contact IntelliHire — Career Platform Support',
  description: 'Contact IntelliHire for platform questions, support, product feedback, and career-preparation assistance.',
  alternates: { canonical: 'https://intellihire-v2.vercel.app/contact' },
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return children;
}
