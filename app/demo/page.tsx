'use client'

import { useState, useEffect } from 'react'
import { getDemo, AnalysisResult } from '@/lib/api'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import LoadingState from '@/components/LoadingState'
import ErrorState from '@/components/ErrorState'
import WalkthroughDisplay from '@/components/WalkthroughDisplay'

export default function DemoPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [demoData, setDemoData] = useState<AnalysisResult | null>(null)

  useEffect(() => {
    loadDemo()
  }, [])

  const loadDemo = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await getDemo()
      setDemoData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load demo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-5xl font-bold mb-4 text-shadow">
              🎮 DEMO WALKTHROUGH
            </h1>
            <p className="text-lg mb-2 font-medium">
              Experience a sample repository analysis
            </p>
            <p className="text-sm text-gray-600 mb-6">
              This demo shows how the AI agent analyzes repositories and generates gamified learning experiences
            </p>
          </div>

          {loading && <LoadingState />}
          {error && <ErrorState error={error} onRetry={loadDemo} />}
          {demoData && !loading && <WalkthroughDisplay result={demoData} />}

          {!loading && !error && !demoData && (
            <div className="card text-center py-12">
              <h3 className="text-xl font-bold mb-4">Demo Not Available</h3>
              <p className="text-gray-600 mb-6">The demo content could not be loaded.</p>
              <button onClick={loadDemo} className="btn-primary">
                Try Again
              </button>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  )
}