import fs from 'node:fs/promises'

async function readSecondFlagHalf() {
  const flag = (await fs.readFile('/flag.txt', 'utf8')).trim()
  return flag.slice(Math.ceil(flag.length / 2))
}

export async function getServerSideProps() {
  return {
    props: {
      backstageNote: await readSecondFlagHalf(),
    },
  }
}

export default function CdnHome({ backstageNote }) {
  return (
    <main className="accepted-background" aria-label="Accepted">
      <div className="flag-overlay">{backstageNote}</div>
    </main>
  )
}
