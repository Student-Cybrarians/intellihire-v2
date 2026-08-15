import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Courses — Placement & Interview Preparation',
  description: 'Follow an AI-guided preparation path across resume optimization, assessments, technical interviews, HR practice, and hiring readiness.',
  alternates: { canonical: 'https://intellihire-v2.vercel.app/courses' },
};

export default function CoursesLayout({ children }: { children: React.ReactNode }) {
  return children;
}
