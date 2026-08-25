'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { ReactNode } from 'react';

const items = [
  { href: '/app', label: 'Workspace' },
  { href: '/app/module1', label: 'Module 1' },
  { href: '/app/module2', label: 'Module 2' },
  { href: '/app/module3', label: 'Module 3' },
  { href: '/app/module4', label: 'Module 4' },
  { href: '/app/module5', label: 'Module 5' },
];

export default function AppShell({ children, name }: { children: ReactNode; name?: string }) {
  const pathname = usePathname();
  return (
    <div className="m3">
      <header>
        <Link href="/app" className="brand" aria-label="Go to IntelliHire workspace">✦ INTELLIHIRE</Link>
        <span>AI CAREER INTELLIGENCE</span>
        <nav aria-label="Application navigation">
          {items.map((item) => {
            const active = item.href === '/app'
              ? pathname === '/app'
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return <Link key={item.href} href={item.href} aria-current={active ? 'page' : undefined} style={{ color: active ? '#eaf1ff' : undefined }}>
              {item.label}
            </Link>;
          })}
          <a href="/api/auth/logout">Sign out</a>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
