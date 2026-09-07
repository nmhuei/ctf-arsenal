"use client";

const { useEffect, useState } = require("react");

function Article({ fetcher }) {
  const [html, setHtml] = useState("<p>loading...</p>");

  useEffect(() => {
    const promise = fetcher();
    promise.then(setHtml)
    promise.catch(() => setHtml("<p class='text-red-500'>Error</p>"))
  }, [fetcher]);

  return <div dangerouslySetInnerHTML={{__html:html}} />
}

export default Article;
