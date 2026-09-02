type RegistrationOptionsJSON = Omit<PublicKeyCredentialCreationOptions, 'challenge' | 'user' | 'excludeCredentials'> & {
  challenge: string;
  user: Omit<PublicKeyCredentialUserEntity, 'id'> & { id: string };
  excludeCredentials?: Array<Omit<PublicKeyCredentialDescriptor, 'id'> & { id: string }>;
};

type RegistrationOptionsEnvelope = {
  publicKey?: RegistrationOptionsJSON;
  state?: unknown;
  error?: string;
} & Partial<RegistrationOptionsJSON>;

function fromBase64Url(value: string): ArrayBuffer {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(value.length / 4) * 4, '=');
  return Uint8Array.from(window.atob(base64), (character) => character.charCodeAt(0)).buffer;
}

function toBase64Url(value: ArrayBuffer): string {
  const bytes = new Uint8Array(value);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return window.btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function decodeOptions(options: RegistrationOptionsJSON): PublicKeyCredentialCreationOptions {
  return {
    ...options,
    challenge: fromBase64Url(options.challenge),
    user: { ...options.user, id: fromBase64Url(options.user.id) },
    excludeCredentials: options.excludeCredentials?.map((credential) => ({
      ...credential,
      id: fromBase64Url(credential.id),
    })),
  };
}

function serializeCredential(credential: PublicKeyCredential) {
  const response = credential.response as AuthenticatorAttestationResponse;
  return {
    id: credential.id,
    rawId: toBase64Url(credential.rawId),
    type: credential.type,
    authenticatorAttachment: credential.authenticatorAttachment,
    clientExtensionResults: credential.getClientExtensionResults(),
    response: {
      clientDataJSON: toBase64Url(response.clientDataJSON),
      attestationObject: toBase64Url(response.attestationObject),
      transports: response.getTransports?.() ?? [],
      publicKey: response.getPublicKey?.() ? toBase64Url(response.getPublicKey() as ArrayBuffer) : null,
      publicKeyAlgorithm: response.getPublicKeyAlgorithm?.() ?? null,
      authenticatorData: response.getAuthenticatorData?.()
        ? toBase64Url(response.getAuthenticatorData())
        : null,
    },
  };
}

async function post<T>(url: string, body: unknown, fallbackError: string): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  const result = await response.json() as T & { error?: string };
  if (!response.ok) throw new Error(result.error ?? fallbackError);
  return result;
}

export async function createPasskey(onProgress: (message: string) => void) {
  if (!window.isSecureContext || !navigator.credentials || !window.PublicKeyCredential) {
    throw new Error('Passkeys require HTTPS or localhost in a supported browser.');
  }

  onProgress('Preparing passkey registration…');
  const envelope = await post<RegistrationOptionsEnvelope>(
    '/api/flag/registration-options',
    { origin: window.location.origin, userAgent: navigator.userAgent },
    'Could not start passkey registration.',
  );
  const options = envelope.publicKey ?? envelope as RegistrationOptionsJSON;
  if (!options.challenge || !options.user?.id) throw new Error('Flag service returned invalid registration options.');

  onProgress('Complete the passkey prompt in your browser…');
  const credential = await navigator.credentials.create({ publicKey: decodeOptions(options) });
  if (!(credential instanceof PublicKeyCredential)) throw new Error('Passkey registration did not return a credential.');

  onProgress('Asking the flag service to validate your passkey…');
  const result = await post<{ flag?: string }>(
    '/api/flag/registration-verify',
    {
      origin: window.location.origin,
      registration: { credential: serializeCredential(credential), state: envelope.state },
    },
    'The flag service rejected the passkey.',
  );
  if (!result.flag) throw new Error('Registration succeeded, but the flag service returned no flag.');
  return result.flag;
}
