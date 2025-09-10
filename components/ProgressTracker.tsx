interface ProgressTrackerProps {
  progress: {
    total_points: number
    current_level: number
    progress_percentage: number
    modules_completed: number
    achievements_unlocked: number
    level_thresholds: number[]
    level_titles: string[]
  }
}

export default function ProgressTracker({ progress }: ProgressTrackerProps) {
  const currentLevelTitle = progress.level_titles[progress.current_level - 1] || 'Code Newbie'
  const nextLevelTitle = progress.level_titles[progress.current_level] || 'Code Wizard'
  const currentThreshold = progress.level_thresholds[progress.current_level - 1] || 0
  const nextThreshold = progress.level_thresholds[progress.current_level] || progress.level_thresholds[progress.level_thresholds.length - 1]
  
  return (
    <div className="border-2 border-black p-6 bg-gray-50">
      <div className="text-center mb-4">
        <h3 className="text-xl font-bold mb-1">
          Level {progress.current_level}: {currentLevelTitle}
        </h3>
        <p className="text-sm text-gray-600">
          {progress.total_points} / {nextThreshold} points to {nextLevelTitle}
        </p>
      </div>

      <div className="mb-4">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress.progress_percentage}%` }}
          ></div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 text-center text-sm">
        <div>
          <div className="text-2xl font-bold">{progress.total_points}</div>
          <div className="text-gray-600">Total Points</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{progress.modules_completed}</div>
          <div className="text-gray-600">Modules Done</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{progress.achievements_unlocked}</div>
          <div className="text-gray-600">Achievements</div>
        </div>
      </div>
    </div>
  )
}