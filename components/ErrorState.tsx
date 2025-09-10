interface ErrorStateProps {
  error: string
  onRetry?: () => void
}

export default function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <div className="card">
      <div className="text-center py-8">
        <div className="mb-4">
          <div className="inline-flex items-center justify-center w-16 h-16 border-4 border-black bg-white">
            <span className="text-2xl">⚠️</span>
          </div>
        </div>
        
        <h3 className="text-lg font-bold mb-2">Analysis Failed</h3>
        <p className="text-sm text-gray-600 mb-6 max-w-md mx-auto">{error}</p>
        
        <div className="space-y-2 text-xs text-gray-500 mb-6">
          <p>Common issues:</p>
          <ul className="list-none space-y-1">
            <li>• Repository is private or doesn&apos;t exist</li>
            <li>• Invalid GitHub URL format</li>
            <li>• Repository is too large or complex</li>
            <li>• Network connection issues</li>
          </ul>
        </div>
        
        {onRetry && (
          <button onClick={onRetry} className="btn-primary">
            Try Again
          </button>
        )}
      </div>
    </div>
  )
}