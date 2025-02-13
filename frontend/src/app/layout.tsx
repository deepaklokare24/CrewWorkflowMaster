import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Lease Exit Workflow Management',
  description: 'AI-powered lease exit workflow management system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background">
            <nav className="border-b">
              <div className="container mx-auto flex h-16 items-center px-4">
                <Link href="/" className="flex items-center space-x-2">
                  <span className="text-xl font-bold">Lease Exit Manager</span>
                </Link>
                <div className="ml-auto flex items-center space-x-4">
                  <Link href="/tasks" className="text-sm font-medium">Tasks</Link>
                  <Link href="/notifications" className="text-sm font-medium">Notifications</Link>
                </div>
              </div>
            </nav>
            <main className="container mx-auto py-6">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  )
}