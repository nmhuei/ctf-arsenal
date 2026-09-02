import { PanelLeftClose } from 'lucide-react';
import { MAX_SOURCE_LENGTH } from '../limits';

type Props = {
  source: string;
  onChange: (source: string) => void;
  onClose: () => void;
};

export function Editor({ source, onChange, onClose }: Props) {
  const lineCount = source.split('\n').length;

  return (
    <section className="editor-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">01 / INPUT</span>
          <h1>Markdown source</h1>
        </div>
        <button className="icon-button" onClick={onClose} aria-label="Hide editor">
          <PanelLeftClose size={18} />
        </button>
      </div>
      <div className="editor-wrap">
        <div className="line-numbers" aria-hidden="true">
          {Array.from({ length: lineCount }, (_, index) => <span key={index}>{index + 1}</span>)}
        </div>
        <textarea
          aria-label="Markdown source"
          spellCheck="false"
          maxLength={MAX_SOURCE_LENGTH}
          value={source}
          onChange={(event) => onChange(event.target.value)}
        />
      </div>
      <div className="editor-footer">
        <span>Markdown + YAML</span>
        <span>{source.length.toLocaleString()} / {MAX_SOURCE_LENGTH.toLocaleString()} characters</span>
      </div>
    </section>
  );
}
