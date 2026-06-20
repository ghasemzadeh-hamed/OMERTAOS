import { useRef, useState, type PointerEvent, type ReactNode } from 'react';
import { Maximize2, Minus, X } from 'lucide-react';
import { APP_BY_ID } from '../lib/apps';
import { useShellStore } from '../lib/shellStore';
import type { ShellWindow } from '../types/shell';

interface WindowFrameProps { windowState: ShellWindow; children: ReactNode }

export function WindowFrame({ windowState, children }: WindowFrameProps) {
  const app = APP_BY_ID.get(windowState.appId)!;
  const Icon = app.icon;
  const closeApp = useShellStore((state) => state.closeApp);
  const focusApp = useShellStore((state) => state.focusApp);
  const toggleMinimize = useShellStore((state) => state.toggleMinimize);
  const toggleMaximize = useShellStore((state) => state.toggleMaximize);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const drag = useRef<{ pointerX: number; pointerY: number; startX: number; startY: number } | null>(null);

  const startDrag = (event: PointerEvent<HTMLDivElement>) => {
    if (windowState.maximized || (event.target as HTMLElement).closest('button')) return;
    drag.current = { pointerX: event.clientX, pointerY: event.clientY, startX: position.x, startY: position.y };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const moveDrag = (event: PointerEvent<HTMLDivElement>) => {
    if (!drag.current) return;
    setPosition({
      x: drag.current.startX + event.clientX - drag.current.pointerX,
      y: drag.current.startY + event.clientY - drag.current.pointerY,
    });
  };

  return (
    <section
      className={`window-frame ${windowState.maximized ? 'maximized' : ''}`}
      style={{ zIndex: windowState.zIndex, transform: windowState.maximized ? undefined : `translate(${position.x}px, ${position.y}px)` }}
      onMouseDown={() => focusApp(windowState.appId)}
      aria-label={`${app.label} window`}
    >
      <div className="window-titlebar" onPointerDown={startDrag} onPointerMove={moveDrag} onPointerUp={() => { drag.current = null; }}>
        <div className="window-title"><Icon size={16} /><strong>{app.windowTitle ?? app.label}</strong></div>
        <div className="window-controls">
          <button onClick={() => toggleMinimize(windowState.appId)} aria-label={`Minimize ${app.label}`}><Minus size={16} /></button>
          <button onClick={() => toggleMaximize(windowState.appId)} aria-label={`Maximize ${app.label}`}><Maximize2 size={14} /></button>
          <button className="close" onClick={() => closeApp(windowState.appId)} aria-label={`Close ${app.label}`}><X size={16} /></button>
        </div>
      </div>
      <div className="window-content">{children}</div>
    </section>
  );
}
