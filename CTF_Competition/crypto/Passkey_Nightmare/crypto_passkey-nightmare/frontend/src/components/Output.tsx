import { useState } from 'react';
import { marked } from 'marked';
import { Braces, Check, CircleAlert, Copy, FileText, Sparkles } from 'lucide-react';
import type { ParsedSource } from '../types';

marked.setOptions({ gfm: true, breaks: true });

type Props = {
  parsed: ParsedSource;
  editorOpen: boolean;
  onShowEditor: () => void;
};

function formatKey(key: string) {
  return key.replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/[-_]/g, ' ').replace(/^./, (c) => c.toUpperCase());
}

function Value({ value }: { value: unknown }) {
  if (Array.isArray(value)) {
    return <div className="tag-list">{value.map((item) => <span className="tag" key={String(item)}>{String(item)}</span>)}</div>;
  }
  if (typeof value === 'boolean') {
    return <span className={`boolean ${value ? 'is-true' : ''}`}>{value ? 'True' : 'False'}</span>;
  }
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}(?:T00:00:00\.000Z)?$/.test(value)) {
    const date = new Date(`${value.slice(0, 10)}T00:00:00`);
    return <span>{date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>;
  }
  if (value && typeof value === 'object') return <code className="inline-json">{JSON.stringify(value)}</code>;
  return <span>{String(value ?? '—')}</span>;
}

export function Output({ parsed, editorOpen, onShowEditor }: Props) {
  const [tab, setTab] = useState<'preview' | 'data'>('preview');
  const [copied, setCopied] = useState(false);
  const entries = Object.entries(parsed.data);

  async function copyJson() {
    await navigator.clipboard.writeText(JSON.stringify(parsed.data, null, 2));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  return (
    <section className="output-panel">
      <div className="output-header">
        <div className="output-title-row">
          {!editorOpen && <button className="show-editor" onClick={onShowEditor}>Show editor</button>}
          <div>
            <span className="panel-kicker">02 / OUTPUT</span>
            <h2>Rendered document</h2>
          </div>
          <div className={`parse-status ${parsed.error ? 'has-error' : ''} ${parsed.loading ? 'is-loading' : ''}`}>
            {parsed.loading ? <Sparkles size={14} /> : parsed.error ? <CircleAlert size={14} /> : <Check size={14} />}
            {parsed.loading ? 'Parsing…' : parsed.error ? 'Parse error' : 'Parsed successfully'}
          </div>
        </div>
        <div className="tabs" role="tablist">
          <button className={tab === 'preview' ? 'active' : ''} onClick={() => setTab('preview')}>
            <FileText size={15} /> Preview
          </button>
          <button className={tab === 'data' ? 'active' : ''} onClick={() => setTab('data')}>
            <Braces size={15} /> Raw data <span className="count">{entries.length}</span>
          </button>
        </div>
      </div>

      <div className="output-scroll">
        {parsed.error ? (
          <div className="error-card">
            <CircleAlert size={22} />
            <div><h3>We couldn't read that frontmatter</h3><p>{parsed.error}</p></div>
          </div>
        ) : tab === 'preview' ? (
          <div className="document">
            <section className="frontmatter-block">
              <div className="section-label">
                <span>Frontmatter</span><span className="rule" /><span>{entries.length} fields</span>
              </div>
              {entries.length ? (
                <div className="meta-grid">
                  {entries.map(([key, value]) => (
                    <div className="meta-item" key={key}>
                      <span className="meta-key">{formatKey(key)}</span>
                      <div className="meta-value"><Value value={value} /></div>
                    </div>
                  ))}
                </div>
              ) : <p className="empty-note">No frontmatter fields found. Add a YAML block between <code>---</code> delimiters.</p>}
            </section>
            <section className="markdown-body" dangerouslySetInnerHTML={{ __html: marked.parse(parsed.content) }} />
          </div>
        ) : (
          <div className="raw-view">
            <div className="raw-toolbar">
              <div><Sparkles size={15} /><span>Parsed frontmatter object</span></div>
              <button onClick={copyJson}>
                {copied ? <Check size={14} /> : <Copy size={14} />}{copied ? 'Copied' : 'Copy JSON'}
              </button>
            </div>
            <pre><code>{JSON.stringify(parsed.data, null, 2)}</code></pre>
          </div>
        )}
      </div>
    </section>
  );
}
