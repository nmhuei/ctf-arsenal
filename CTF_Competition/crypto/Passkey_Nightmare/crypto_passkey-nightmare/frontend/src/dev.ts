import { spawn } from 'node:child_process';

const command = process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm';
const api = spawn(command, ['exec', 'tsx', 'src/server.ts'], { stdio: 'inherit' });
const web = spawn(command, ['exec', 'vite'], { stdio: 'inherit' });
let stopping = false;

function stop(signal: NodeJS.Signals = 'SIGTERM') {
  if (stopping) return;
  stopping = true;
  api.kill(signal);
  web.kill(signal);
}

api.on('exit', (code) => {
  if (!stopping) {
    stop();
    process.exitCode = code ?? 1;
  }
});

web.on('exit', (code) => {
  if (!stopping) {
    stop();
    process.exitCode = code ?? 1;
  }
});

process.on('SIGINT', () => stop('SIGINT'));
process.on('SIGTERM', () => stop('SIGTERM'));
