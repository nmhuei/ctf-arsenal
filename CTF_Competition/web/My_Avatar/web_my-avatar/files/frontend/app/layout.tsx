import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MyAvatar — Identity Forge",
  description: "Forge, watermark, and archive a louder digital identity.",
  icons: {
    icon: "/og.png",
    shortcut: "/og.png",
  },
  openGraph: {
    title: "MyAvatar — Identity Forge",
    description: "Forge, watermark, and archive a louder digital identity.",
    type: "website",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "MyAvatar Identity Forge" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "MyAvatar — Identity Forge",
    description: "Forge, watermark, and archive a louder digital identity.",
    images: ["/og.png"],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
