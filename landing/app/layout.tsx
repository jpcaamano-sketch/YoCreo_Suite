import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "YoCreo IA - Suite de Liderazgo Consciente",
  description:
    "14 prácticas de coaching asistidas por Inteligencia Artificial para potenciar tu liderazgo, comunicación y productividad.",
  openGraph: {
    title: "YoCreo IA - Suite de Liderazgo Consciente",
    description:
      "14 prácticas de coaching con IA para líderes y equipos.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
