import { CircleAlert, KeyRound, LoaderCircle, X } from 'lucide-react';
import type { FlagState } from '../types';

type Props = {
  state: FlagState;
  onDismiss: () => void;
};

export function FlagNotice({ state, onDismiss }: Props) {
  if (state.status === 'idle') return null;

  const title = state.status === 'success'
    ? 'Flag acquired'
    : state.status === 'error' ? 'Registration failed' : 'Passkey registration';

  return (
    <aside className={`flag-notice ${state.status}`} role={state.status === 'error' ? 'alert' : 'status'}>
      <div className="flag-notice-icon">
        {state.status === 'loading'
          ? <LoaderCircle className="spin" size={18} />
          : state.status === 'success' ? <KeyRound size={18} /> : <CircleAlert size={18} />}
      </div>
      <div><span>{title}</span><strong>{state.message}</strong></div>
      {state.status !== 'loading' && (
        <button onClick={onDismiss} aria-label="Dismiss"><X size={15} /></button>
      )}
    </aside>
  );
}
