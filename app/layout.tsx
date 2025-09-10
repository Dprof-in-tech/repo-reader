import './globals.css'
import { Inter } from 'next/font/google'
import { QuizProvider } from '@/lib/quiz-context'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Repo Reader - AI Repository Analysis',
  description: 'AI-powered repository analysis and gamified code walkthroughs',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QuizProvider>
          {children}
        </QuizProvider>
      </body>
    </html>
  )
}
