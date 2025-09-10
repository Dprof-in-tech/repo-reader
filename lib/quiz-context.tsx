'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'

interface QuizStats {
  totalQuizzesTaken: number
  perfectScores: number
  currentStreak: number
  bestStreak: number
  totalPointsEarned: number
  averageScore: number
  quizHistory: Array<{
    moduleId: string
    score: number
    attempts: number
    timestamp: number
  }>
}

interface QuizContextType {
  stats: QuizStats
  updateQuizResult: (moduleId: string, score: number, attempts: number) => void
  resetStats: () => void
}

const defaultStats: QuizStats = {
  totalQuizzesTaken: 0,
  perfectScores: 0,
  currentStreak: 0,
  bestStreak: 0,
  totalPointsEarned: 0,
  averageScore: 0,
  quizHistory: []
}

const QuizContext = createContext<QuizContextType | null>(null)

export function QuizProvider({ children }: { children: React.ReactNode }) {
  const [stats, setStats] = useState<QuizStats>(() => {
    // Load from localStorage if available
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('repo-reader-quiz-stats')
      if (saved) {
        try {
          return JSON.parse(saved)
        } catch (e) {
          console.warn('Failed to parse saved quiz stats')
        }
      }
    }
    return defaultStats
  })

  const updateQuizResult = useCallback((moduleId: string, score: number, attempts: number) => {
    setStats(prevStats => {
      const isPerfect = score === 100
      let newStreak = isPerfect ? prevStats.currentStreak + 1 : 0
      
      const newHistory = [
        ...prevStats.quizHistory,
        { moduleId, score, attempts, timestamp: Date.now() }
      ]

      const totalScores = newHistory.reduce((sum, quiz) => sum + quiz.score, 0)
      const averageScore = Math.round(totalScores / newHistory.length)

      const newStats = {
        totalQuizzesTaken: prevStats.totalQuizzesTaken + 1,
        perfectScores: prevStats.perfectScores + (isPerfect ? 1 : 0),
        currentStreak: newStreak,
        bestStreak: Math.max(prevStats.bestStreak, newStreak),
        totalPointsEarned: prevStats.totalPointsEarned + (score * 50 / 100), // Approximate points
        averageScore,
        quizHistory: newHistory
      }

      // Save to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('repo-reader-quiz-stats', JSON.stringify(newStats))
      }

      return newStats
    })
  }, [])

  const resetStats = useCallback(() => {
    setStats(defaultStats)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('repo-reader-quiz-stats')
    }
  }, [])

  return (
    <QuizContext.Provider value={{ stats, updateQuizResult, resetStats }}>
      {children}
    </QuizContext.Provider>
  )
}

export function useQuiz() {
  const context = useContext(QuizContext)
  if (!context) {
    throw new Error('useQuiz must be used within a QuizProvider')
  }
  return context
}