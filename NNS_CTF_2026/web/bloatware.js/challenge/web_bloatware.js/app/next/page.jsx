import Article from "@/components/article";
import Link from "@/components/link";


import { getNextHtml } from "@/fetch";

export default function Next() {
  return (
    <>
      <h1>Blötwar!</h1>
      <ul><li><Link path="/">Home</Link></li></ul>
      <Article fetcher={getNextHtml} />
    </>
  );
}
