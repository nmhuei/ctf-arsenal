import { createJwt } from '../../lib/jwt'
import { createUser } from '../../lib/users'

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end()

  try {
    const user = await createUser(String(req.body.username || ''), String(req.body.password || ''))
    const sessionToken = await createJwt(user)
    res.setHeader('Set-Cookie', [
      `session=${encodeURIComponent(sessionToken)}; Path=/; HttpOnly; SameSite=Lax`,
      `ticket_uuid=${encodeURIComponent(user.ticketUuid)}; Path=/; HttpOnly; SameSite=Lax`,
    ])
    res.redirect(302, `/access-card?id=${user.id}`)
  } catch (error) {
    res.status(400).send(error.message)
  }
}
