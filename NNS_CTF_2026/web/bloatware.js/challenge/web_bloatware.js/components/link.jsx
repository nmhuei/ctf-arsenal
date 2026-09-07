"use client";

export default function Link({ path, children }) {
  return <a onClick={() => {
        if (typeof window === "undefined") return;
        window.location.href = `${window.location.origin}${path}`
  }}>{children}</a>
}
