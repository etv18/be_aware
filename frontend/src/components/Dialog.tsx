import { useEffect, useRef, type ReactNode } from 'react';

/**
 * The native <dialog class="modal"> (a bottom sheet on a phone). Its children only exist while it is open, so a form
 * inside starts fresh every time. Esc, the X button and a click outside all end up in onClose.
 */
export function Dialog({ open, onClose, children }: { open: boolean; onClose: () => void; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog ref={ref} className="modal" onClose={onClose} onMouseDown={(event) => { if (event.target === ref.current) onClose(); }}>
      {open ? children : null}
    </dialog>
  );
}
