import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Clinic-Specific AI Dental Screening",
  description: "AI-assisted dental screening & patient record prototype",
};

import { ToastProvider } from "@/components/ui/Toast";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {apiUrl && <link rel="preconnect" href={apiUrl} />}
      </head>
      <body className="min-h-full flex flex-col bg-surface text-foreground">
        <ToastProvider>
          <Breadcrumbs />
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
