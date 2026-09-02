import fs from 'node:fs/promises'

export async function readFirstFlagHalf() {
  const flag = (await fs.readFile('/flag.txt', 'utf8')).trim()
  return flag.slice(0, Math.ceil(flag.length / 2))
}
