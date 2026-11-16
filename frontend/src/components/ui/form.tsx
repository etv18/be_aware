// Forms in a dialog. (partials/ui.html: form_dialog, field, amount_field, date_field, text_field, select_field, method_field)
//
//   <FormDialog open title="New expense" onClose={...} onSubmit={save}>
//     <AmountField value={values.amount} onChange={(v) => set('amount', v)} />
//     ...
//   </FormDialog>
//
// onSubmit does the saving and throws what the server answered (ApiError). A message about one field shows under that
// field; any other message goes in the banner at the top.
import { Children, cloneElement, createContext, isValidElement, useContext, useEffect, useRef, useState, type FormEvent, type ReactElement, type ReactNode } from 'react';

import { Dialog } from '@/components/Dialog';
import { Icon } from '@/components/Icon';
import { ApiError } from '@/lib/api';

// what the server said per field, and which fields are on screen (to know what is left for the banner)
const FieldErrors = createContext<{ messages: Record<string, string>; shown: Set<string> }>({ messages: {}, shown: new Set() });

export function FormDialog({ open, title, onClose, onSubmit, children }: {
  open: boolean; title: string; onClose: () => void; onSubmit: () => Promise<void>; children: ReactNode;
}) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const shown = useRef(new Set<string>());

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSubmit();
    } catch (caught) {
      if (!(caught instanceof ApiError)) throw caught;
      setError(caught);
    } finally {
      setSaving(false);
    }
  }

  const messages = error?.fields ?? {};
  const names = Object.keys(messages);
  const banner = error && (names.length === 0 || names.some((name) => !shown.current.has(name))) ? error.message : null;

  return (
    <Dialog open={open} onClose={onClose}>
      <form noValidate onSubmit={submit}>
        <div className="flex items-center justify-between border-b border-line px-5 py-3.5">
          <h2 className="text-base font-semibold">{title}</h2>
          <button type="button" className="btn-icon -mr-1.5" aria-label="Close" onClick={onClose}><Icon name="x" /></button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-5 py-4">
          {banner && <p className="mb-4 rounded-lg border border-negative/30 bg-negative/10 px-3 py-2 text-sm text-negative" role="alert">{banner}</p>}
          <FieldErrors.Provider value={{ messages, shown: shown.current }}>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
          </FieldErrors.Provider>
        </div>
        <div className="flex justify-end gap-2 border-t border-line px-5 py-3.5">
          <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>Save</button>
        </div>
      </form>
    </Dialog>
  );
}

/** One labelled field with its error line. `half`: half width on a wide screen. The single child is the input. */
export function Field({ name, label, half = false, optional = false, children }: {
  name: string; label: string; half?: boolean; optional?: boolean; children: ReactNode;
}) {
  const { messages, shown } = useContext(FieldErrors);
  const message = messages[name];
  useEffect(() => {
    shown.add(name);
    return () => { shown.delete(name); };
  }, [shown, name]);
  const child = Children.only(children);
  const input = isValidElement(child)
    ? cloneElement(child as ReactElement<Record<string, unknown>>, { id: `f-${name}`, name, ...(message ? { 'aria-invalid': 'true' } : {}) })
    : child;

  return (
    <div className={half ? '' : 'sm:col-span-2'}>
      <label className="label" htmlFor={`f-${name}`}>{label}{optional && <> <span className="font-normal text-faint">(optional)</span></>}</label>
      {input}
      {message && <p className="field-error">{message}</p>}
    </div>
  );
}

type Controlled = { value: string; onChange: (value: string) => void };

export function AmountField({ value, onChange, label = 'Amount', name = 'amount' }: Controlled & { label?: string; name?: string }) {
  return (
    <Field name={name} label={label} half>
      <input className="input num" type="text" inputMode="decimal" autoComplete="off" placeholder="0.00" required value={value} onChange={(e) => onChange(e.target.value)} />
    </Field>
  );
}

export function DateField({ value, onChange, label = 'Date and time', name = 'created_at' }: Controlled & { label?: string; name?: string }) {
  return (
    <Field name={name} label={label} half>
      <input className="input" type="datetime-local" required value={value} onChange={(e) => onChange(e.target.value)} />
    </Field>
  );
}

export function TextField({ name, label, value, onChange, optional, half, placeholder }: Controlled & {
  name: string; label: string; optional?: boolean; half?: boolean; placeholder?: string;
}) {
  return (
    <Field name={name} label={label} optional={optional} half={half}>
      <input className="input" type="text" autoComplete="off" placeholder={placeholder} required={!optional} value={value} onChange={(e) => onChange(e.target.value)} />
    </Field>
  );
}

export function SelectField({ name, label, value, onChange, items, blank, half }: Controlled & {
  name: string; label: string; items: { id: number; label: string }[]; blank: string; half?: boolean;
}) {
  return (
    <Field name={name} label={label} half={half}>
      <select className="select" required value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">{blank}</option>
        {items.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
      </select>
    </Field>
  );
}

/** "Cash | Bank account | Credit card": a row of exclusive choices. */
export function MethodField<V extends string>({ label, value, onChange, options, name = 'method' }: {
  label: string; value: V; onChange: (value: V) => void; options: [V, string][]; name?: string;
}) {
  return (
    <div className="sm:col-span-2">
      <span className="label">{label}</span>
      <div className="segmented" role="radiogroup" aria-label={label}>
        {options.map(([optionValue, text]) => (
          <label key={optionValue}>
            <input className="peer sr-only" type="radio" name={name} value={optionValue} checked={value === optionValue} onChange={() => onChange(optionValue)} />
            <span>{text}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
