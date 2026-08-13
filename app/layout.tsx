import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'IntelliHire — AI Technical Interview Simulator', description: 'Simulated technical interview platform.' };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
