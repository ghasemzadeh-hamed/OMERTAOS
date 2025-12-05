import { ensureConsoleAccess } from '@/lib/consoleAccess';
import AionLiquidGlassConsole from '@/components/liquid-glass/AionLiquidGlassConsole';

export default async function LiquidConsolePage() {
  await ensureConsoleAccess();
  return <AionLiquidGlassConsole />;
}
