import { createJwt } from '../../lib/jwt'
import { findByUsername, verifyPassword } from '../../lib/users'

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end()

  const user = await findByUsername(String(req.body.username || ''))
  if (!user || !(await verifyPassword(user, String(req.body.password || '')))) {
    return res.status(401).send('invalid backstage login')
  }

  const sessionToken = await createJwt(user)
  res.setHeader('Set-Cookie', [
    `session=${encodeURIComponent(sessionToken)}; Path=/; HttpOnly; SameSite=Lax`,
    `ticket_uuid=${encodeURIComponent(user.ticketUuid)}; Path=/; HttpOnly; SameSite=Lax`,
  ])
  res.redirect(302, `/access-card?id=${user.id}`)
}
