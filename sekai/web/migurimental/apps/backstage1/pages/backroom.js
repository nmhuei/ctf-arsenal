import { readFirstFlagHalf } from '../lib/flag'
import { findByTicketUuid } from '../lib/users'

export async function getServerSideProps({ req, res }) {
  const ticketUser = await findByTicketUuid(req.cookies.ticket_uuid || '')

  if (ticketUser?.id !== 1) {
    res.statusCode = 403
    return {
      props: {
        backstageNote: '',
        denied: true,
      },
    }
  }

  return {
    props: {
      backstageNote: await readFirstFlagHalf(),
      denied: false,
    },
  }
}

export default function Backroom({ backstageNote, denied }) {
  if (denied) {
    return <main className="rejected-background" aria-label="Rejected" />
  }

  return (
    <main className="accepted-background" aria-label="Accepted">
      <div className="flag-overlay">{backstageNote}</div>
    </main>
  )
}
