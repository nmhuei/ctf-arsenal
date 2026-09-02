import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { Editor } from './components/Editor';
import { FlagNotice } from './components/FlagNotice';
import { Header } from './components/Header';
import { Output } from './components/Output';
import { SAMPLE } from './sample';
import { useFlag } from './useFlag';
import { useParsedSource } from './useParsedSource';

export function App() {
  const [source, setSource] = useState(SAMPLE);
  const [editorOpen, setEditorOpen] = useState(true);
  const parsed = useParsedSource(source);
  const { flagState, getFlag, dismissFlag } = useFlag();

  return (
    <div className="app-shell">
      <Header
        flagLoading={flagState.status === 'loading'}
        onReset={() => setSource(SAMPLE)}
        onGetFlag={getFlag}
      />

      <main className={`workspace ${editorOpen ? '' : 'editor-collapsed'}`}>
        {editorOpen && (
          <Editor source={source} onChange={setSource} onClose={() => setEditorOpen(false)} />
        )}
        <Output parsed={parsed} editorOpen={editorOpen} onShowEditor={() => setEditorOpen(true)} />
      </main>

      <footer>
        <span>Parse. Inspect. Render.</span>
        <span className="footer-mark">MM / 2026 <ChevronDown size={13} /></span>
      </footer>

      <FlagNotice state={flagState} onDismiss={dismissFlag} />
    </div>
  );
}
