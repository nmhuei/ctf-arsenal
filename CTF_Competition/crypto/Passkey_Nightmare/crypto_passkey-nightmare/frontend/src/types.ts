export type ParsedSource = {
  data: Record<string, unknown>;
  content: string;
  error: string | null;
  loading: boolean;
};

export type FlagState = {
  status: 'idle' | 'loading' | 'success' | 'error';
  message?: string;
};
