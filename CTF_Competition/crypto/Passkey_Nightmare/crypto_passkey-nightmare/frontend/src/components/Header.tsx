import { KeyRound, LoaderCircle, RotateCcw } from 'lucide-react';

type Props = {
  flagLoading: boolean;
  onReset: () => void;
  onGetFlag: () => void;
};

export function Header({ flagLoading, onReset, onGetFlag }: Props) {
  return (
    <header className="topbar">
      <a className="brand" href="#" aria-label="Mattermark home">
        <span className="brand-mark"><span>M</span></span>
        <span className="brand-name">mattermark</span>
      </a>
      <div className="topbar-center">
        <span className="eyebrow">Frontmatter renderer</span>
        <span className="divider" />
        <span className="powered">Powered by <strong>gray-matter</strong></span>
      </div>
      <div className="topbar-actions">
        <button className="sample-button" onClick={onReset}>
          <RotateCcw size={14} /> Reset sample
        </button>
        <button className="flag-button" disabled={flagLoading} onClick={onGetFlag}>
          {flagLoading ? <LoaderCircle className="spin" size={15} /> : <KeyRound size={15} />}
          {flagLoading ? 'Registering…' : 'Get flag'}
        </button>
      </div>
    </header>
  );
}
