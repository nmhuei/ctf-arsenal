import { NextResponse } from 'next/server'
import { verifyJwt } from './lib/jwt'

function deny(request) {
  return NextResponse.redirect(new URL('/failed', request.url), 302)
}

export async function middleware(request) {
  const session = await verifyJwt(request.cookies.get('session')?.value)

  if (!session?.sub) {
    return deny(request)
  }

  if (request.nextUrl.pathname === '/access-card') {
    const checkedId = request.nextUrl.searchParams.get('id')
    
    if (checkedId !== session.sub) {
      return deny(request)
    }
  }

  if (request.nextUrl.pathname === '/backroom') {
    const expectedTicket = session.ticketUuid
    const middlewareTicket = request.cookies.get('ticket_uuid')?.value || ''

    if (!expectedTicket || middlewareTicket !== expectedTicket) {
      return deny(request)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/access-card', '/backroom'],
}
