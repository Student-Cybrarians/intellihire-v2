import './globals.css';
import type { Metadata } from 'next';

const siteUrl = 'https://intellihire-v2.vercel.app';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'IntelliHire — AI Career Intelligence & Placement Trainer',
    template: '%s | IntelliHire',
  },
  description:
    'IntelliHire is an AI-powered career intelligence and placement training platform for resume optimization, adaptive assessments, technical interviews, HR practice, and hiring readiness.',
  applicationName: 'IntelliHire',
  keywords: [
    'AI career intelligence',
    'placement preparation',
    'resume optimization',
    'ATS resume checker',
    'adaptive assessment',
    'technical interview preparation',
    'HR interview preparation',
    'hiring readiness',
    'career roadmap',
    'AI placement trainer',
  ],
  authors: [{ name: 'IntelliHire' }],
  creator: 'IntelliHire',
  publisher: 'IntelliHire',
  alternates: { canonical: siteUrl },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
      'max-video-preview': -1,
    },
  },
  openGraph: {
    type: 'website',
    url: siteUrl,
    siteName: 'IntelliHire',
    title: 'IntelliHire — AI Career Intelligence & Placement Trainer',
    description:
      'Train smarter with AI-powered resume intelligence, adaptive assessments, technical interviews, HR practice, and hiring readiness.',
    locale: 'en_IN',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'IntelliHire — AI Career Intelligence & Placement Trainer',
    description:
      'AI-powered resume intelligence, assessments, interview preparation, and career readiness.',
  },
};

const structuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      '@id': `${siteUrl}/#organization`,
      name: 'IntelliHire',
      url: siteUrl,
      description:
        'AI-powered career intelligence and placement training platform.',
    },
    {
      '@type': 'WebSite',
      '@id': `${siteUrl}/#website`,
      name: 'IntelliHire',
      url: siteUrl,
      description:
        'AI-powered career intelligence, placement preparation, and hiring readiness.',
      publisher: { '@id': `${siteUrl}/#organization` },
      inLanguage: 'en-IN',
    },
    {
      '@type': 'SoftwareApplication',
      name: 'IntelliHire',
      applicationCategory: 'EducationalApplication',
      operatingSystem: 'Web',
      url: siteUrl,
      description:
        'AI-based placement trainer covering resume intelligence, adaptive assessment, technical interviews, HR preparation, and hiring readiness.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'INR' },
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-IN">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
