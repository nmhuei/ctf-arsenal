"use cache";

const nameToUrl = (name) =>
  `https://en.wikipedia.org/w/rest.php/v1/page/${name}/html`;

async function getBloatwareHtml() {
  const response = await fetch(nameToUrl("Software_bloat"));
  return await response.text();
}

async function getNextHtml() {
  const response = await fetch(nameToUrl("Next.js"));
  return (await response.text()).replaceAll("Next.js", "bloatware.js");
}

export { getBloatwareHtml, getNextHtml }
