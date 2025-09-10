export default function LoadingState() {
  return (
    <div className="card">
      <div className="text-center py-12">
        <div className="mb-6">
          <div className="inline-block w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
        </div>
        
        <h3 className="text-lg font-bold mb-4">Analyzing Repository</h3>
        
        <div className="space-y-2 text-sm text-gray-600 max-w-md mx-auto">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-black rounded-full animate-bounce"></div>
            <span>Cloning repository</span>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <span>Analyzing code structure</span>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <span>Generating walkthrough</span>
          </div>
        </div>
        
        <div className="mt-6">
          <div className="progress-bar">
            <div className="progress-fill animate-pulse" style={{ width: '45%' }}></div>
          </div>
          <p className="text-xs text-gray-500 mt-2">This usually takes 30-60 seconds</p>
        </div>
      </div>
    </div>
  )
}