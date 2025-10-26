import "./globals.css";
import type { Metadata } from "next";
import { Manrope } from "next/font/google";
import { ReactNode } from "react";

const manrope = Manrope({ subsets: ["latin"], variable: "--font-manrope" });

export const metadata: Metadata = {
  title: "LeafCheck",
  description: "Assess greenwashing risk with LeafCheck"
};

export default function RootLayout({
  children
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en" className="bg-background-light">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"
        />
      </head>
      <body className={`${manrope.className} bg-background-light text-dark-grey`}>
        {children}
      </body>
    </html>
  );
}
