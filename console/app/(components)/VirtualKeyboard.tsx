'use client';

import { useEffect, useRef, useState } from 'react';
import Keyboard from 'react-simple-keyboard';
import 'simple-keyboard/build/css/index.css';

type KeyboardLayout = 'default' | 'shift' | 'numbers';

type Props = {
  bindTo?: string;
  rtl?: boolean;
  layoutName?: KeyboardLayout;
  onClose?: () => void;
};

const baseLayout = {
  default: ['q w e r t y u i o p', 'a s d f g h j k l', 'z x c v b n m .', '{numbers} {space} {bksp} {enter} {shift} {close}'],
  shift: ['Q W E R T Y U I O P', 'A S D F G H J K L', 'Z X C V B N M .', '{numbers} {space} {bksp} {enter} {shift} {close}'],
  numbers: ['1 2 3 4 5 6 7 8 9 0 - /', '@ # $ _ & - + ( ) *', '" \" : ; ! ?', '{default} {space} {bksp} {enter} {close}'],
};

const display = {
  '{bksp}': 'Backspace',
  '{enter}': 'Enter',
  '{shift}': 'Shift',
  '{space}': 'Space',
  '{numbers}': '123',
  '{default}': 'ABC',
  '{close}': 'Close',
};

const insertBackspace = (element: HTMLInputElement | HTMLTextAreaElement | HTMLElement) => {
  if ((element as HTMLInputElement | HTMLTextAreaElement).value !== undefined) {
    const input = element as HTMLInputElement | HTMLTextAreaElement;
    const start = input.selectionStart ?? input.value.length;
    const end = input.selectionEnd ?? input.value.length;
    if (start === end && start > 0) {
      input.value = `${input.value.slice(0, start - 1)}${input.value.slice(end)}`;
      const caret = start - 1;
      input.setSelectionRange?.(caret, caret);
    } else {
      input.value = `${input.value.slice(0, start)}${input.value.slice(end)}`;
      input.setSelectionRange?.(start, start);
    }
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return;
  }

  if ((element as HTMLElement).isContentEditable) {
    document.execCommand('delete', false);
  }
};

const insertText = (
  element: HTMLInputElement | HTMLTextAreaElement | (HTMLElement & { isContentEditable?: boolean }),
  text: string,
) => {
  if ((element as HTMLInputElement | HTMLTextAreaElement).value !== undefined) {
    const input = element as HTMLInputElement | HTMLTextAreaElement;
    const start = input.selectionStart ?? input.value.length;
    const end = input.selectionEnd ?? input.value.length;
    input.value = `${input.value.slice(0, start)}${text}${input.value.slice(end)}`;
    const caret = start + text.length;
    input.setSelectionRange?.(caret, caret);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return;
  }

  if ((element as HTMLElement).isContentEditable) {
    document.execCommand('insertText', false, text);
  }
};

export default function VirtualKeyboard({
  bindTo = '#chat-input',
  rtl = false,
  layoutName = 'default',
  onClose,
}: Props) {
  const [currentLayout, setCurrentLayout] = useState<KeyboardLayout>(layoutName);
  const [isRtl, setIsRtl] = useState(rtl);
  const inputRef = useRef<
    HTMLInputElement | HTMLTextAreaElement | (HTMLElement & { isContentEditable?: boolean }) | null
  >(null);

  useEffect(() => {
    inputRef.current = document.querySelector(bindTo) as typeof inputRef.current;
  }, [bindTo]);

  useEffect(() => {
    setCurrentLayout(layoutName);
  }, [layoutName]);

  useEffect(() => {
    setIsRtl(rtl);
  }, [rtl]);

  const handleKeyPress = (button: string) => {
    const target = inputRef.current;
    if (!target) return;

    if (button === '{bksp}') {
      insertBackspace(target);
      return;
    }

    if (button === '{space}') {
      insertText(target, ' ');
      return;
    }

    if (button === '{enter}') {
      insertText(target, '\n');
      target.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
      return;
    }

    if (button === '{shift}') {
      setCurrentLayout((prev) => (prev === 'default' ? 'shift' : 'default'));
      return;
    }

    if (button === '{numbers}') {
      setCurrentLayout('numbers');
      return;
    }

    if (button === '{default}') {
      setCurrentLayout('default');
      return;
    }

    if (button === '{close}') {
      onClose?.();
      return;
    }

    insertText(target, button);
  };

  return (
    <div
      dir={isRtl ? 'rtl' : 'ltr'}
      className="fixed bottom-0 left-0 right-0 z-[60] border-t border-white/10 bg-black/20 backdrop-blur-md"
    >
      <div className="flex items-center justify-between px-3 py-2">
        <button
          type="button"
          className="min-h-[44px] min-w-[44px] rounded-md px-2 py-1"
          onClick={() => setIsRtl((prev) => !prev)}
        >
          {isRtl ? 'RTL' : 'LTR'}
        </button>
        <span className="text-xs opacity-70">Virtual Keyboard</span>
        <button
          type="button"
          className="min-h-[44px] min-w-[44px] rounded-md px-2 py-1"
          onClick={() => onClose?.()}
        >
          Close
        </button>
      </div>
      <Keyboard
        layout={baseLayout}
        layoutName={currentLayout}
        display={display}
        onKeyPress={handleKeyPress}
        rtl={isRtl}
      />
    </div>
  );
}
