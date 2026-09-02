import { SignJWT, jwtVerify } from 'jose'

const JWT_SECRET = process.env.BACKSTAGE_JWT_SECRET
const JWT_KEY = new TextEncoder().encode(JWT_SECRET)

function getJwtKey() {
  return JWT_KEY
}

export async function createJwt(user) {
  return new SignJWT({
    username: user.username,
    tier: user.tier,
    ticketUuid: user.ticketUuid,
  })
    .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
    .setSubject(String(user.id))
    .setIssuedAt()
    .sign(getJwtKey())
}

export async function verifyJwt(token) {
  if (!token) return null

  try {
    const { payload } = await jwtVerify(token, getJwtKey(), {
      algorithms: ['HS256'],
    })
    return payload
  } catch {
    return null
  }
}
