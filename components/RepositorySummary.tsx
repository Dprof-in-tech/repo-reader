interface RepositorySummaryProps {
  repoData: {
    repo_name: string
    github_url: string
    languages: string[]
    frameworks: string[]
    files: Array<{
      path: string
      language: string
      size: number
    }>
    key_files: Array<{
      name: string
      type: string
      path: string
    }>
  }
  analysisData: {
    complexity_score: number
    architecture_pattern: string
    entry_points: Array<{
      file: string
      type: string
      language: string
    }>
    key_components: Array<{
      file: string
      language: string
      type: string
      complexity: number
    }>
    dependencies: Array<{
      name: string
      version: string
      type: string
    }>
    code_quality: {
      documentation_score: number
      test_coverage_estimate: number
      code_organization: string
      naming_consistency: string
    }
  }
  summary: {
    repository: string
    architecture: string
    complexity_score: number
    learning_modules: number
    estimated_time: string
  }
}

export default function RepositorySummary({ repoData, analysisData, summary }: RepositorySummaryProps) {
  const getComplexityColor = (score: number) => {
    if (score < 30) return 'text-green-600'
    if (score < 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getQualityColor = (quality: string | number) => {
    const qualityStr = String(quality || '').toLowerCase()
    switch (qualityStr) {
      case 'good': return 'text-green-600'
      case 'fair': return 'text-yellow-600'
      case 'poor': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold mb-2">📊 Repository Analysis</h3>
          <a 
            href={repoData.github_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm text-gray-600 hover:text-black font-mono break-all"
          >
            {repoData.github_url}
          </a>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">{analysisData.complexity_score}/100</div>
          <div className="text-xs text-gray-600">Complexity</div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div>
          <h4 className="font-bold mb-2">🏗️ Architecture</h4>
          <p className="text-sm">{analysisData.architecture_pattern}</p>
        </div>
        
        
        <div>
          <h4 className="font-bold mb-2">⚡ Frameworks</h4>
          <div className="flex flex-wrap gap-1">
            {repoData.frameworks.length > 0 ? (
              repoData.frameworks.map((framework, index) => (
                <span 
                  key={index} 
                  className="text-xs bg-gray-100 px-2 py-1 border border-black"
                >
                  {framework}
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-500">None detected</span>
            )}
          </div>

          <div className="mt-4">
          <h4 className="font-bold mb-2">💻 Languages</h4>
          <div className="flex flex-wrap gap-1">
            {repoData.languages.map((lang, index) => (
              <span 
                key={index} 
                className="text-xs bg-gray-100 px-2 py-1 border border-black"
              >
                {lang}
              </span>
            ))}
          </div>
        </div>
        </div>
        
        <div>
          <h4 className="font-bold mb-2">📈 Quality</h4>
          <div className="text-sm space-y-1">
            <div className={getQualityColor(analysisData.code_quality.code_organization)}>
              {String(analysisData.code_quality.code_organization || 'Unknown')} Organization
            </div>
            <div>
              {analysisData.code_quality.test_coverage_estimate}% Test Coverage
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div>
          <h4 className="font-bold mb-3">🚪 Entry Points</h4>
          <div className="space-y-2">
            {analysisData.entry_points.slice(0, 3).map((entry, index) => (
              <div key={index} className="text-sm">
                <div className="font-mono text-xs bg-gray-50 px-2 py-1 border border-gray-200">
                  {entry.file}
                </div>
                <div className="text-xs text-gray-600">{entry.type}</div>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h4 className="font-bold mb-3">🧩 Key Components</h4>
          <div className="space-y-2">
            {analysisData.key_components.slice(0, 3).map((component, index) => (
              <div key={index} className="text-sm">
                <div className="font-mono text-xs bg-gray-50 px-2 py-1 border border-gray-200">
                  {component.file.split('/').pop()}
                </div>
                <div className="text-xs text-gray-600">{component.type}</div>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h4 className="font-bold mb-3">📦 Dependencies</h4>
          <div className="space-y-1">
            {analysisData.dependencies.slice(0, 4).map((dep, index) => (
              <div key={index} className="text-xs">
                <span className="font-medium">{dep.name}</span>
                <span className="text-gray-600 ml-1">v{dep.version}</span>
              </div>
            ))}
            {analysisData.dependencies.length > 4 && (
              <div className="text-xs text-gray-500">
                +{analysisData.dependencies.length - 4} more
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="mt-6 pt-4 border-t-2 border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
          <div>
            <div className="text-lg font-bold">{repoData.files.length}</div>
            <div className="text-gray-600">Files</div>
          </div>
          <div>
            <div className="text-lg font-bold">{repoData.key_files.length}</div>
            <div className="text-gray-600">Config Files</div>
          </div>
          <div>
            <div className={`text-lg font-bold ${getComplexityColor(analysisData.complexity_score)}`}>
              {analysisData.complexity_score}
            </div>
            <div className="text-gray-600">Complexity</div>
          </div>
          <div>
            <div className="text-lg font-bold">{summary.learning_modules}</div>
            <div className="text-gray-600">Modules</div>
          </div>
        </div>
      </div>
    </div>
  )
}