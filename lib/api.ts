const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:5328' 
  : 'http://localhost:5328' // Update this for production

export interface AnalysisResult {
  success: boolean
  error?: string
  repo_data?: {
    repo_name: string
    github_url: string
    languages: string[]
    frameworks: string[]
    files: Array<{
      path: string
      language: string
      size: number
      content: string
    }>
    key_files: Array<{
      name: string
      type: string
      path: string
      content: string
    }>
  }
  analysis_data?: {
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
      dependencies: string[]
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
    learning_path: Array<{
      step: number
      title: string
      description: string
      difficulty: string
      estimated_time: string
      focus_files: string[]
    }>
  }
  walkthrough_data?: {
    title: string
    description: string
    difficulty_level: {
      level: string
      stars: string
      complexity_score: number
      user_adjusted: boolean
    }
    estimated_completion_time: string
    achievements: Array<{
      id: string
      title: string
      description: string
      points: number
      unlocked: boolean
    }>
    learning_modules: Array<{
      id: string
      title: string
      description: string
      difficulty: string
      estimated_time: string
      learning_objectives: string[]
      activities: Array<{
        type: string
        title: string
        description: string
        instructions: string[]
        expected_discoveries?: number
        expected_patterns?: number
        expected_traces?: number
        points: number
      }>
      quiz: Array<{
        type: string
        question: string
        options?: string[]
        correct: number | boolean
        sample_answer?: string
        explanation: string
      }>
      resources: string[]
      unlocked: boolean
      completion_criteria: {
        read_files: number
        answer_quiz: number
        activities_completed: number
      }
    }>
    progress_tracking: {
      total_points: number
      current_level: number
      progress_percentage: number
      modules_completed: number
      achievements_unlocked: number
      level_thresholds: number[]
      level_titles: string[]
    }
    interactive_elements: {
      code_snippets: Array<{
        file: string
        language: string
        snippet: string
        explanation: string
      }>
      interactive_diagrams: {
        architecture_overview: boolean
        component_relationships: boolean
        data_flow: boolean
      }
      live_code_exploration: {
        enabled: boolean
        supported_languages: string[]
        syntax_highlighting: boolean
      }
      progress_visualization: {
        progress_bar: boolean
        achievement_badges: boolean
        level_indicators: boolean
        completion_celebrations: boolean
      }
    }
    gamification_elements: {
      point_system: {
        file_read: number
        quiz_correct: number
        activity_complete: number
        module_complete: number
        achievement_unlock: number
      }
      streaks: {
        daily_learning: number
        perfect_quiz: number
        module_completion: number
      }
      social_features: {
        leaderboard: boolean
        sharing: boolean
        progress_sharing: boolean
      }
      rewards: {
        virtual_badges: boolean
        completion_certificates: boolean
        skill_endorsements: boolean
      }
    }
  }
  processing_summary?: {
    repository: string
    architecture: string
    complexity_score: number
    learning_modules: number
    estimated_time: string
  }
}

export async function analyzeRepository(
  githubUrl: string, 
  userLevel: 'beginner' | 'intermediate' | 'advanced'
): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      github_url: githubUrl,
      user_level: userLevel,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export interface StreamingResponse {
  task_id: string
  stream_url: string
  status: string
}

export interface ProgressMessage {
  role: string
  content: string
  timestamp: number
}

export async function analyzeRepositoryStreaming(
  githubUrl: string, 
  userLevel: 'beginner' | 'intermediate' | 'advanced',
  onProgress?: (message: ProgressMessage) => void
): Promise<AnalysisResult> {
  // Start streaming analysis
  const initResponse = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      github_url: githubUrl,
      user_level: userLevel,
      stream: true,
    }),
  })

  if (!initResponse.ok) {
    const errorData = await initResponse.json().catch(() => ({}))
    throw new Error(errorData.error || `HTTP ${initResponse.status}: ${initResponse.statusText}`)
  }

  const streamData: StreamingResponse = await initResponse.json()
  
  // Connect to streaming endpoint
  return new Promise((resolve, reject) => {
    const eventSource = new EventSource(`${API_BASE_URL}${streamData.stream_url}`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'progress') {
          if (onProgress) {
            onProgress(data.message)
          }
        } else if (data.type === 'complete') {
          eventSource.close()
          if (data.result.success) {
            resolve(data.result)
          } else {
            reject(new Error(data.result.error || 'Analysis failed'))
          }
        }
      } catch (err) {
        console.error('Error parsing stream data:', err)
      }
    }
    
    eventSource.onerror = (error) => {
      eventSource.close()
      reject(new Error('Stream connection failed'))
    }
  })
}

export async function getDemo(): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/demo`)
  
  if (!response.ok) {
    throw new Error(`Failed to load demo: ${response.statusText}`)
  }

  return await response.json()
}

export async function getStatus() {
  const response = await fetch(`${API_BASE_URL}/api/status`)
  
  if (!response.ok) {
    throw new Error(`Failed to get status: ${response.statusText}`)
  }

  return await response.json()
}

export interface CodeQuestionResult {
  success: boolean
  error?: string
  answer?: string
  sources?: Array<{
    file_path: string
    lines: string
    language: string
    similarity_score: number
  }>
  search_results?: any[]
  context_used?: number
  user_level?: string
}

export async function askCodeQuestion(
  question: string,
  repoName: string,
  userLevel: string = 'intermediate'
): Promise<CodeQuestionResult> {
  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      repo_name: repoName,
      user_level: userLevel
    })
  })

  if (!response.ok) {
    throw new Error(`Failed to ask question: ${response.statusText}`)
  }

  return await response.json()
}

export interface CodeSearchResult {
  success: boolean
  error?: string
  query?: string
  repo_name?: string
  search_type?: string
  results_count?: number
  results?: Array<{
    file_path: string
    chunk_id: string
    content: string
    full_content: string
    metadata: any
    search_type: string
    similarity_score?: number
    relevance_score?: number
    combined_score?: number
  }>
}

export async function searchCode(
  query: string,
  repoName: string,
  searchType: 'vector' | 'fulltext' | 'hybrid' = 'hybrid',
  limit: number = 5
): Promise<CodeSearchResult> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      repo_name: repoName,
      search_type: searchType,
      limit
    })
  })

  if (!response.ok) {
    throw new Error(`Failed to search code: ${response.statusText}`)
  }

  return await response.json()
}