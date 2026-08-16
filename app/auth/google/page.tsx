import { redirect } from 'next/navigation';

export default function GoogleSignInPage() {
  redirect('/api/auth/google');
}
