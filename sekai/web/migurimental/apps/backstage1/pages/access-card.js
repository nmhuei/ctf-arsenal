import { findById } from '../lib/users'
import QRCode from 'qrcode'

export async function getServerSideProps({ query }) {
  const user = await findById(query.id)
  if (!user) return { notFound: true }
  const qrDataUrl = await QRCode.toDataURL(user.ticketUuid, {
    errorCorrectionLevel: 'M',
    margin: 1,
    width: 220,
    color: {
      dark: '#06111a',
      light: '#ffffffff',
    },
  })

  return {
    props: {
      user: {
        id: user.id,
        username: user.username,
        tier: user.tier,
      },
      qrDataUrl,
    },
  }
}

export default function AccessCard({ user, qrDataUrl }) {
  return (
    <main>
      <section className="panel card">
        <div className="photo">{user.username.slice(0, 1).toUpperCase()}</div>
        <div>
          <h1>Concert Access Card</h1>
          <p className="muted">Username</p>
          <h2>{user.username}</h2>
          <p className="muted">Ticket tier</p>
          <p>
            <span className="tier">{user.tier}</span>
          </p>
          <a className="button" href="/backroom">Enter Backroom</a>
        </div>
        <div className="qr">
          <img src={qrDataUrl} alt="Ticket QR" />
        </div>
      </section>
    </main>
  )
}
