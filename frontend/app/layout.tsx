import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Financial Asset Relationship Network',
  description: 'Interactive 3D visualization of interconnected financial assets',
}

/**
 * Root layout component that provides the top-level HTML skeleton and renders application content.
 *
 * Sets the document language to `"en"` and places `children` inside the `<body>` element.
 *
 * @param children - The React node(s) to render as the page content inside the document body
 */
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