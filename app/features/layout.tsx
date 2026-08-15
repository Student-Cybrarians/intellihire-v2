import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Features — Resume, Assessment & Interview Intelligence',
  description: 'Explore IntelliHire capabilities for ATS resume intelligence, adaptive assessment, technical interviews, HR practice, hiring readiness, and admin intelligence.',
  alternates: { canonical: 'https://intellihire-v2.vercel.app/features' },
};

export default function FeaturesLayout({ children }: { children: React.ReactNode }) {
  return children;
}
