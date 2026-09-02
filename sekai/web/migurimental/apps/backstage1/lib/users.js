import crypto from 'node:crypto'
import fs from 'node:fs/promises'
import bcrypt from 'bcryptjs'
import sqlite3 from 'sqlite3'
import { open } from 'sqlite'

const DB_DIR = '/app/apps/backstage1/data'
const DB_PATH = '/app/apps/backstage1/data/backstage.sqlite'

let dbPromise

async function database() {
  if (!dbPromise) {
    await fs.mkdir(DB_DIR, { recursive: true })
    dbPromise = open({
      filename: DB_PATH,
      driver: sqlite3.Database,
    })
  }
  return dbPromise
}

export async function createSchema() {
  const db = await database()
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
}

export async function seedDefaults() {
  await createSchema()
  const db = await database()

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
}

function rowToUser(row) {
  if (!row) return null
  return {
    id: row.id,
    username: row.username,
    passwordHash: row.password_hash,
    tier: row.tier,
    ticketUuid: row.ticket_uuid,
  }
}

export async function findById(id) {
  await createSchema()
  const db = await database()
  const row = await db.get('SELECT * FROM users WHERE id = ?', [id])
  return rowToUser(row)
}

export async function findByUsername(username) {
  await createSchema()
  const db = await database()
  const row = await db.get('SELECT * FROM users WHERE username = ?', [username])
  return rowToUser(row)
}

export async function findByTicketUuid(ticketUuid) {
  await createSchema()
  const db = await database()
  const row = await db.get('SELECT * FROM users WHERE ticket_uuid = ?', [ticketUuid])
  return rowToUser(row)
}

export async function createUser(username, password) {
  await createSchema()
  if (!username || !password) throw new Error('username and password are required')
  if (username.length < 3 || username.length > 32) {
    throw new Error('username must be between 3 and 32 characters')
  }
  if (password.length < 8 || password.length > 128) {
    throw new Error('password must be between 8 and 128 characters')
  }

  const db = await database()
  const ticketUuid = crypto.randomUUID()
  const passwordHash = await bcrypt.hash(password, 12)

  try {
    const result = await db.run(
      `
        INSERT INTO users (username, password_hash, tier, ticket_uuid)
        VALUES (?, ?, ?, ?)
      `,
      [username, passwordHash, 'REGULAR', ticketUuid]
    )
    return findById(result.lastID)
  } catch (error) {
    if (String(error.message || '').includes('UNIQUE')) {
      throw new Error('username already exists')
    }
    throw error
  }
}

export async function verifyPassword(user, password) {
  if (!user?.passwordHash || !password) return false
  return bcrypt.compare(password, user.passwordHash)
}
