import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import bcrypt from 'bcryptjs'
import sqlite3 from 'sqlite3'
import { open } from 'sqlite'

const dbDir = '/app/apps/backstage1/data'
const dbPath = '/app/apps/backstage1/data/backstage.sqlite'

await fs.mkdir(dbDir, { recursive: true })

const db = await open({
  filename: dbPath,
  driver: sqlite3.Database,
})

await db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('REGULAR', 'VIP')),
    ticket_uuid TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
`)

await db.run(
  `
    INSERT INTO users (id, username, password_hash, tier, ticket_uuid)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      password_hash = excluded.password_hash,
      ticket_uuid = excluded.ticket_uuid
  `,
  [1, 'miku', await bcrypt.hash(crypto.randomUUID(), 12), 'VIP', crypto.randomUUID()]
)

await db.run(
  `
    INSERT INTO users (id, username, password_hash, tier, ticket_uuid)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      password_hash = excluded.password_hash,
      ticket_uuid = excluded.ticket_uuid
  `,
  [2, 'audience', await bcrypt.hash(crypto.randomUUID(), 12), 'REGULAR', crypto.randomUUID()]
)

await db.close()
console.log('backstage sqlite database initialized')
