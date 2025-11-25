import { redirect } from 'next/navigation';
import { safeGetServerSession } from '@/lib/session';
import AionLiquidGlassConsole from '@/components/liquid-glass/AionLiquidGlassConsole';

export default async function LiquidConsolePage() {
  const session = await safeGetServerSession();

  if (!session) {
    redirect('/login');
  }

  return <AionLiquidGlassConsole />;
}
