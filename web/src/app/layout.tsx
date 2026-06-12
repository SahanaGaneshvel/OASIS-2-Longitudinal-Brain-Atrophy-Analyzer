import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OASIS-2 Brain Atrophy Analyzer',
  description: 'Longitudinal brain atrophy analysis in aging and Alzheimer\'s disease',
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
