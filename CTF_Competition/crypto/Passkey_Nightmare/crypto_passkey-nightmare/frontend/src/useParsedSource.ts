import { useEffect, useState } from 'react';
import type { ParsedSource } from './types';

const PARSE_DEBOUNCE_MS = 300;

export function useParsedSource(source: string) {
  const [parsed, setParsed] = useState<ParsedSource>({
    data: {},
    content: '',
    error: null,
    loading: true,
  });

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setParsed((current) => ({ ...current, loading: true }));

      try {
        const response = await fetch('/api/parse', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source }),
          signal: controller.signal,
        });
        const result = await response.json() as {
          data?: Record<string, unknown>;
          content?: string;
          error?: string;
        };

        if (!response.ok) throw new Error(result.error || 'Unable to parse frontmatter.');
        setParsed({ data: result.data ?? {}, content: result.content ?? '', error: null, loading: false });
      } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
          setParsed({
            data: {},
            content: '',
            error: error instanceof Error ? error.message : 'Unable to parse frontmatter.',
            loading: false,
          });
        }
      }
    }, PARSE_DEBOUNCE_MS);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [source]);

  return parsed;
}
