'use client'

import { useState } from 'react'
import { analyzeRepository, analyzeRepositoryStreaming, AnalysisResult, ProgressMessage } from '@/lib/api'
import LoadingState from '@/components/LoadingState'
import ErrorState from '@/components/ErrorState'
import WalkthroughDisplay from '@/components/WalkthroughDisplay'
import StreamingProgress from '@/components/StreamingProgress'

export default function RepositoryAnalyzer() {
  const [url, setUrl] = useState('')
  const [userLevel, setUserLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('beginner')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [progressMessages, setProgressMessages] = useState<ProgressMessage[]>([])
  const [useStreaming, setUseStreaming] = useState(true)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a GitHub repository URL')
      return
    }
    
    // Basic URL validation
    if (!url.includes('github.com') || !url.includes('/')) {
      setError('Please enter a valid GitHub repository URL')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    setProgressMessages([])

    try {
      if (useStreaming) {
        const analysisResult = await analyzeRepositoryStreaming(
          url.trim(), 
          userLevel,
          (message: ProgressMessage) => {
            setProgressMessages(prev => [...prev, message])
          }
        )
        setResult(analysisResult)
      } else {
        const analysisResult = await analyzeRepository(url.trim(), userLevel)
        setResult(analysisResult)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setUrl('')
    setUserLevel('beginner')
    setError(null)
    setResult(null)
    setProgressMessages([])
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Input Form */}
      <div className="card mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="url" className="block text-sm font-medium mb-2">
              GitHub Repository URL
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="input-field"
              disabled={loading}
              required
            />
            <p className="text-xs text-gray-600 mt-1">
              Enter a public GitHub repository URL to analyze
            </p>
          </div>

          <div>
            <label htmlFor="level" className="block text-sm font-medium mb-2">
              Your Experience Level
            </label>
            <select
              id="level"
              value={userLevel}
              onChange={(e) => setUserLevel(e.target.value as 'beginner' | 'intermediate' | 'advanced')}
              className="input-field"
              disabled={loading}
            >
              <option value="beginner">Beginner - New to coding</option>
              <option value="intermediate">Intermediate - Some experience</option>
              <option value="advanced">Advanced - Experienced developer</option>
            </select>
            <p className="text-xs text-gray-600 mt-1">
              This helps customize the walkthrough difficulty
            </p>
          </div>

          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useStreaming}
                onChange={(e) => setUseStreaming(e.target.checked)}
                className="w-4 h-4 border-2 border-black focus:ring-2 focus:ring-black"
                disabled={loading}
              />
              <span className="text-sm font-medium">
                Show real-time progress (recommended)
              </span>
            </label>
            <p className="text-xs text-gray-600 mt-1">
              Watch the git clone progress and analysis in real-time
            </p>
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="loading-dots">Analyzing</span>
              ) : (
                'Analyze Repository'
              )}
            </button>
            
            {(result || error) && (
              <button
                type="button"
                onClick={handleReset}
                className="btn-secondary"
                disabled={loading}
              >
                Reset
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Streaming Progress */}
      {useStreaming && (progressMessages.length > 0 || loading) && (
        <StreamingProgress 
          messages={progressMessages} 
          isActive={loading}
        />
      )}

      {/* Loading State (for non-streaming mode) */}
      {!useStreaming && loading && <LoadingState />}

      {/* Error State */}
      {error && <ErrorState error={error} onRetry={() => handleSubmit(new Event('submit') as any)} />}

      {/* Results */}
      {result && !loading && <WalkthroughDisplay result={result} />}
    </div>
  )
}