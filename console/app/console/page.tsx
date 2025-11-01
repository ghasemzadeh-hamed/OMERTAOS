import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import AionLiquidGlassConsole from '@/components/liquid-glass/AionLiquidGlassConsole';

export default async function LiquidConsolePage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect('/login');
  }

  return <AionLiquidGlassConsole />;
}
