import { redirect } from 'next/navigation';

export default function FaLoginRedirect() {
  redirect('/login?locale=fa');
}
