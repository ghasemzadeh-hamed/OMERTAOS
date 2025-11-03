"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import VirtualKeyboard from "@/app/(components)/VirtualKeyboard";

type Props = {
  children: ReactNode;
};

export default function TouchProvider({ children }: Props) {
  const [showVK, setShowVK] = useState(false);

  const enabled = process.env.NEXT_PUBLIC_ENABLE_VK !== "false";

  useEffect(() => {
    if (!enabled) return;

    const isTouch = typeof window !== "undefined" && matchMedia("(pointer: coarse)").matches;
    if (!isTouch) return;

    const onFocus = (event: Event) => {
      const target = event.target as HTMLElement | null;
      if (!target) return;

      const tag = target.tagName;
      const editable = (target as HTMLElement & { isContentEditable?: boolean }).isContentEditable;
      if (tag === "INPUT" || tag === "TEXTAREA" || editable) {
        setShowVK(true);
      }
    };

    const onBlur = () => setShowVK(false);

    window.addEventListener("focusin", onFocus);
    window.addEventListener("focusout", onBlur);

    return () => {
      window.removeEventListener("focusin", onFocus);
      window.removeEventListener("focusout", onBlur);
    };
  }, [enabled]);

  if (!enabled) {
    return <>{children}</>;
  }

  return (
    <>
      {children}
      {showVK && (
        <VirtualKeyboard bindTo="#chat-input" rtl={true} onClose={() => setShowVK(false)} />
      )}
    </>
  );
}
