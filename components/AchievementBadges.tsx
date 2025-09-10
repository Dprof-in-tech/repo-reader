'use client'

import { useState, useEffect } from 'react'

interface Achievement {
  id: string
  title: string
  description: string
  points: number
  unlocked: boolean
}

interface AchievementBadgesProps {
  achievements: Achievement[]
  onAchievementUnlock?: (points: number) => void
}

export default function AchievementBadges({ achievements, onAchievementUnlock }: AchievementBadgesProps) {
  const [localAchievements, setLocalAchievements] = useState(achievements)
  const [newlyUnlocked, setNewlyUnlocked] = useState<string | null>(null)

  const unlockAchievement = (id: string) => {
    const achievement = localAchievements.find(a => a.id === id)
    if (achievement && !achievement.unlocked) {
      setLocalAchievements(prev => 
        prev.map(a => a.id === id ? { ...a, unlocked: true } : a)
      )
      setNewlyUnlocked(id)
      onAchievementUnlock?.(achievement.points)
      
      // Clear the notification after 3 seconds
      setTimeout(() => setNewlyUnlocked(null), 3000)
    }
  }

  useEffect(() => {
    // Auto-unlock first achievement when component mounts
    const firstAchievement = localAchievements.find(a => a.id === 'first_steps')
    if (firstAchievement && !firstAchievement.unlocked) {
      setTimeout(() => unlockAchievement('first_steps'), 1000)
    }
  }, [])

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4">🏆 Achievements</h3>
      
      {/* Newly unlocked notification */}
      {newlyUnlocked && (
        <div className="mb-4 p-3 border-2 border-black bg-yellow-50 animate-pulse">
          <p className="text-sm font-medium">🎉 Achievement Unlocked!</p>
          <p className="text-xs">
            {localAchievements.find(a => a.id === newlyUnlocked)?.title}
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {localAchievements.map((achievement) => (
          <div
            key={achievement.id}
            className={`p-4 border-2 text-center transition-all duration-200 ${
              achievement.unlocked
                ? 'border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
                : 'border-gray-300 bg-gray-100 opacity-50'
            }`}
          >
            <div className="text-2xl mb-2">
              {achievement.unlocked ? '🏆' : '🔒'}
            </div>
            <h4 className={`text-sm font-bold mb-1 ${
              achievement.unlocked ? 'text-black' : 'text-gray-500'
            }`}>
              {achievement.title}
            </h4>
            <p className={`text-xs mb-2 ${
              achievement.unlocked ? 'text-gray-600' : 'text-gray-400'
            }`}>
              {achievement.description}
            </p>
            <div className={`text-xs font-medium ${
              achievement.unlocked ? 'text-black' : 'text-gray-400'
            }`}>
              {achievement.points} pts
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center text-sm text-gray-600">
        <p>
          {localAchievements.filter(a => a.unlocked).length} / {localAchievements.length} unlocked
        </p>
      </div>
    </div>
  )
}