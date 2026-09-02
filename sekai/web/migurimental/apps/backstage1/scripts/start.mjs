import crypto from 'node:crypto'
import { spawn } from 'node:child_process'

process.env.BACKSTAGE_JWT_SECRET = crypto.randomBytes(32).toString('base64url')

const child = spawn('npm', ['run', 'start'], {
  stdio: 'inherit',
  env: process.env,
})

child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal)
  process.exit(code ?? 0)
})
