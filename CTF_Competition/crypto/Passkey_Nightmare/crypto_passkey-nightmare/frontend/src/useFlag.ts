import { useState } from 'react';
import { createPasskey } from './passkeys';
import type { FlagState } from './types';

export function useFlag() {
  const [flagState, setFlagState] = useState<FlagState>({ status: 'idle' });

  async function getFlag() {
    try {
      const flag = await createPasskey((message) => setFlagState({ status: 'loading', message }));
      setFlagState({ status: 'success', message: flag });
    } catch (error) {
      const message = error instanceof DOMException && error.name === 'NotAllowedError'
        ? 'Passkey registration was cancelled or timed out.'
        : error instanceof Error ? error.message : 'Passkey registration failed.';
      setFlagState({ status: 'error', message });
    }
  }

  return {
    flagState,
    getFlag,
    dismissFlag: () => setFlagState({ status: 'idle' }),
  };
}
