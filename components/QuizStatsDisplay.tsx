'use client'

import { useQuiz } from '@/lib/quiz-context'

export default function QuizStatsDisplay() {
  const { stats, resetStats } = useQuiz()

  if (stats.totalQuizzesTaken === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-bold mb-2">📊 Quiz Statistics</h3>
        <p className="text-sm text-gray-600">Complete your first quiz to see statistics!</p>
      </div>
    )
  }

  const accuracyRate = Math.round((stats.perfectScores / stats.totalQuizzesTaken) * 100)

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">📊 Quiz Statistics</h3>
        <button
          onClick={resetStats}
          className="text-xs text-gray-500 hover:text-red-600 transition-colors"
          title="Reset all quiz statistics"
        >
          🗑️ Reset
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 border border-gray-200">
          <div className="text-xl font-bold text-blue-600">{stats.totalQuizzesTaken}</div>
          <div className="text-xs text-gray-600">Quizzes Taken</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 border border-gray-200">
          <div className="text-xl font-bold text-green-600">{stats.averageScore}%</div>
          <div className="text-xs text-gray-600">Average Score</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 border border-gray-200">
          <div className="text-xl font-bold text-purple-600">{stats.currentStreak}</div>
          <div className="text-xs text-gray-600">Current Streak</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 border border-gray-200">
          <div className="text-xl font-bold text-orange-600">{stats.bestStreak}</div>
          <div className="text-xs text-gray-600">Best Streak</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="font-medium">Perfect Scores:</span>
          <span className="ml-2">{stats.perfectScores}/{stats.totalQuizzesTaken}</span>
        </div>
        <div>
          <span className="font-medium">Accuracy Rate:</span>
          <span className={`ml-2 font-medium ${
            accuracyRate >= 80 ? 'text-green-600' : 
            accuracyRate >= 60 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {accuracyRate}%
          </span>
        </div>
      </div>

      {stats.bestStreak >= 5 && (
        <div className="mt-4 p-3 bg-yellow-50 border-2 border-yellow-300">
          <p className="text-sm font-medium text-yellow-800">
            🏆 Quiz Legend! You&apos;ve achieved a {stats.bestStreak}-quiz perfect streak!
          </p>
        </div>
      )}
    </div>
  )
}