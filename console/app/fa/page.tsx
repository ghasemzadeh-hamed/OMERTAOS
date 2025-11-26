import { redirect } from 'next/navigation';

export default function PersianHomeRedirect() {
  redirect('/?locale=fa');
}
