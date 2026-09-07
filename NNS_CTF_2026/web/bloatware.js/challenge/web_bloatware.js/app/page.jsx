import Article from "@/components/article";
import Link from "@/components/link";


import { getBloatwareHtml } from "@/fetch";

export default async function Home() {
  return (
    <>
      <h1>Meow!</h1>
      <ul><li><Link path="/next">Detail</Link></li></ul>
      <Article fetcher={getBloatwareHtml} />
    </>
  );
}
