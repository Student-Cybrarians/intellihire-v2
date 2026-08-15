import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'IntelliHire — Train Smarter. Interview Better. Get Hired.',
  description: 'AI-powered placement training, resume intelligence, adaptive assessments, interview practice and career readiness.',
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
