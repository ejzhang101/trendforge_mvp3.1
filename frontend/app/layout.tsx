import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TrendForge - AI-Powered YouTube Trend Analysis',
  description: 'Intelligent YouTube trend prediction with deep content analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
