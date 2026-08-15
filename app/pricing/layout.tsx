import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Pricing — IntelliHire',
  description: 'Explore IntelliHire access and pricing for AI-powered placement preparation and career intelligence.',
  alternates: { canonical: 'https://intellihire-v2.vercel.app/pricing' },
};

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return children;
}
