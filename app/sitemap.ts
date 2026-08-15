import type { MetadataRoute } from 'next';

const siteUrl = 'https://intellihire-v2.vercel.app';

export default function sitemap(): MetadataRoute.Sitemap {
  const pages = [
    '',
    '/features',
    '/courses',
    '/pricing',
    '/about',
    '/contact',
    '/faq',
  ];

  return pages.map((path) => ({
    url: `${siteUrl}${path}`,
    lastModified: new Date(),
    changeFrequency: path === '' ? 'weekly' : 'monthly',
    priority: path === '' ? 1 : 0.7,
  }));
}
