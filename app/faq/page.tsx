import type { Metadata } from 'next';
import MarketingShell from '../marketing/MarketingShell';
import styles from '../marketing/marketing.module.css';

export const metadata: Metadata = {
  title: 'FAQ — AI Career Intelligence & Placement Training',
  description:
    'Answers about IntelliHire AI analysis, resume and job-description alignment, candidate evidence, and administrator visibility.',
  alternates: { canonical: 'https://intellihire-v2.vercel.app/faq' },
};

const faqs = [
  {
    question: 'What does the AI actually analyze?',
    answer:
      'Resume and job-description alignment, skills, evidence, assessment performance, and interview responses, depending on the module.',
  },
  {
    question: 'Will it invent skills for my resume?',
    answer:
      'No. Missing requirements can be surfaced as preparation targets or verification items rather than fabricated claims.',
  },
  {
    question: 'Can admins see candidate history?',
    answer:
      "Authorized administrators can use the platform's server-side role controls to review candidate performance and support activity.",
  },
];

const faqSchema = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map(({ question, answer }) => ({
    '@type': 'Question',
    name: question,
    acceptedAnswer: { '@type': 'Answer', text: answer },
  })),
};

export default function FAQ() {
  return (
    <MarketingShell active="faq">
      <section className={styles.faqStrip}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
        <div className={styles.sectionHead}>
          <span>FAQ</span>
          <h1>Clear answers before you commit your time.</h1>
          <p>IntelliHire is designed as a preparation system, not a black-box hiring oracle.</p>
        </div>
        <div className={styles.cards}>
          {faqs.map((faq) => (
            <article className={styles.feature} key={faq.question}>
              <h2>{faq.question}</h2>
              <p>{faq.answer}</p>
            </article>
          ))}
        </div>
      </section>
    </MarketingShell>
  );
}
