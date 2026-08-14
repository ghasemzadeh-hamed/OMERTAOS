import { redirect } from 'next/navigation';

export default function FaWizardRedirect() {
  redirect('/wizard?locale=fa');
}
