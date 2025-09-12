'use client'

import { useState } from 'react'
import { AnalysisResult } from '@/lib/api'
import ProgressTracker from '@/components/ProgressTracker'
import AchievementBadges from '@/components/AchievementBadges'
import LearningModule from '@/components/LearningModule'
import RepositorySummary from '@/components/RepositorySummary'
import QuizStatsDisplay from '@/components/QuizStatsDisplay'
import CodeChatWidget from '@/components/CodeChatWidget'

interface WalkthroughDisplayProps {
  result: AnalysisResult
}

export default function WalkthroughDisplay({ result }: WalkthroughDisplayProps) {
  const [activeModule, setActiveModule] = useState<string | null>(null)
  const [completedModules, setCompletedModules] = useState<Set<string>>(new Set())
  const [progress, setProgress] = useState(result.walkthrough_data?.progress_tracking || {
    total_points: 0,
    current_level: 1,
    progress_percentage: 0,
    modules_completed: 0,
    achievements_unlocked: 1,
    level_thresholds: [0, 500, 1200, 2000, 3000, 4500],
    level_titles: ['Code Newbie', 'Junior Explorer', 'Code Detective', 'Architecture Analyst', 'System Master', 'Code Wizard']
  })

  if (!result.success || !result.walkthrough_data) {
    return (
      <div className="card">
        <p className="text-center text-red-600">Failed to generate walkthrough</p>
      </div>
    )
  }

  const { walkthrough_data, repo_data, analysis_data, processing_summary } = result

  const updateProgress = (points: number) => {
    setProgress(prev => {
      const newTotalPoints = prev.total_points + points
      const newLevel = prev.level_thresholds.findIndex(threshold => newTotalPoints < threshold) || prev.level_thresholds.length
      const currentThreshold = prev.level_thresholds[newLevel - 1] || 0
      const nextThreshold = prev.level_thresholds[newLevel] || prev.level_thresholds[prev.level_thresholds.length - 1]
      const progressInLevel = ((newTotalPoints - currentThreshold) / (nextThreshold - currentThreshold)) * 100

      return {
        ...prev,
        total_points: newTotalPoints,
        current_level: Math.max(newLevel, 1),
        progress_percentage: Math.min(progressInLevel, 100),
        modules_completed: completedModules.size
      }
    })
  }

  const handleModuleComplete = (moduleId: string, points: number) => {
    // Mark module as completed
    setCompletedModules(prev => {
      const newCompleted = new Set(prev)
      newCompleted.add(moduleId)
      return newCompleted
    })
    
    // Update progress
    updateProgress(points)
  }

  const isModuleUnlocked = (moduleIndex: number, moduleId: string) => {
    // First module is always unlocked
    if (moduleIndex === 0) return true
    
    // Check if previous module is completed
    const previousModuleId = walkthrough_data.learning_modules[moduleIndex - 1]?.id
    return previousModuleId ? completedModules.has(previousModuleId) : false
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="card">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold mb-2">{walkthrough_data.title}</h2>
          <p className="text-gray-600 mb-4">{walkthrough_data.description}</p>
          
          <div className="flex justify-center items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <span className="font-medium">Difficulty:</span>
              <span className="text-lg">{walkthrough_data.difficulty_level.stars}</span>
              <span>{walkthrough_data.difficulty_level.level}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-medium">Time:</span>
              <span>{walkthrough_data.estimated_completion_time}</span>
            </div>
          </div>
        </div>

        <ProgressTracker progress={progress} />
      </div>

      {/* Repository Summary */}
      {(repo_data && analysis_data && processing_summary) && (
        <RepositorySummary 
          repoData={repo_data} 
          analysisData={analysis_data}
          summary={processing_summary}
        />
      )}

      {/* Achievements */}
      <AchievementBadges 
        achievements={walkthrough_data.achievements} 
        onAchievementUnlock={(points) => updateProgress(points)}
      />

      {/* Quiz Statistics */}
      <QuizStatsDisplay />

      {/* Learning Modules */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">Learning Modules</h3>
        
        {walkthrough_data.learning_modules.map((module, index) => (
          <LearningModule
            key={module.id}
            module={module}
            isActive={activeModule === module.id}
            isUnlocked={isModuleUnlocked(index, module.id)}
            isCompleted={completedModules.has(module.id)}
            onToggle={() => setActiveModule(activeModule === module.id ? null : module.id)}
            onComplete={(points) => handleModuleComplete(module.id, points)}
          />
        ))}
      </div>

      {/* Code Snippets */}
      {walkthrough_data.interactive_elements.code_snippets.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4">🔍 Key Code Snippets</h3>
          <div className="space-y-4">
            {walkthrough_data.interactive_elements.code_snippets.slice(0, 3).map((snippet, index) => (
              <div key={index} className="border-2 border-gray-200 p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium">{snippet.file}</h4>
                  <span className="text-xs bg-gray-100 px-2 py-1 border border-black">
                    {snippet.language}
                  </span>
                </div>
                <pre className="text-xs bg-gray-50 p-3 border border-gray-200 overflow-x-auto font-mono">
                  <code>{snippet.snippet}</code>
                </pre>
                <p className="text-xs text-gray-600 mt-2">{snippet.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      <div className="card bg-gray-50">
        <h3 className="text-xl font-bold mb-4">🎯 Ready to Start?</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium mb-2">What You&apos;ll Learn:</h4>
            <ul className="text-sm space-y-1 list-none">
              <li>• {analysis_data?.architecture_pattern} architecture</li>
              <li>• {repo_data?.languages.join(', ')} programming</li>
              <li>• {repo_data?.frameworks.join(', ')} frameworks</li>
              <li>• Code organization patterns</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Your Progress:</h4>
            <ul className="text-sm space-y-1 list-none">
              <li>• Level: {progress.level_titles[progress.current_level - 1]}</li>
              <li>• Points: {progress.total_points}</li>
              <li>• Modules: {progress.modules_completed}/{walkthrough_data.learning_modules.length}</li>
              <li>• Achievements: {progress.achievements_unlocked}/{walkthrough_data.achievements.length}</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Code Chat Widget */}
      <CodeChatWidget 
        repoName={result.repo_data?.repo_name || null}
        isVisible={true}
      />
    </div>
  )
}