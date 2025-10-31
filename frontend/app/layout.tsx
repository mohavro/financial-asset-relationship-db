import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Financial Asset Relationship Network',
  description: 'Interactive 3D visualization of interconnected financial assets',
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
