'use client'

import { useState } from 'react'
import { useQuiz } from '@/lib/quiz-context'

interface LearningModuleProps {
  module: {
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
      points: number
    }>
    quiz: Array<{
      type: string
      question: string
      options?: string[]
      correct: number | boolean
      explanation: string
      sample_answer?: string
    }>
    resources: string[]
    unlocked: boolean
    completion_criteria: {
      read_files: number
      answer_quiz: number
      activities_completed: number
    }
  }
  isActive: boolean
  isUnlocked: boolean
  isCompleted?: boolean
  onToggle: () => void
  onComplete: (points: number) => void
}

export default function LearningModule({ 
  module, 
  isActive, 
  isUnlocked, 
  isCompleted = false,
  onToggle, 
  onComplete 
}: LearningModuleProps) {
  const [completedActivities, setCompletedActivities] = useState<string[]>([])
  const [quizAnswers, setQuizAnswers] = useState<Record<number, any>>({})
  const [showQuizResults, setShowQuizResults] = useState(false)
  const [quizScore, setQuizScore] = useState<{
    correct: number
    total: number
    percentage: number
    pointsEarned: number
    attempts: number
    streak: number
  } | null>(null)
  const [quizAttempts, setQuizAttempts] = useState(0)
  const [perfectStreak, setPerfectStreak] = useState(0)
  const [isModuleCompleted, setIsModuleCompleted] = useState(isCompleted)
  const { stats, updateQuizResult } = useQuiz()

  // Helper function to check if a question was answered correctly
  const isQuestionCorrect = (question: any, index: number) => {
    const userAnswer = quizAnswers[index]
    
    if (question.type === 'short_answer') {
      // For short answer questions, use the same logic as in submitQuiz
      const answer = String(userAnswer || '').trim().toLowerCase()
      const sampleAnswer = String(question.sample_answer || '').trim().toLowerCase()
      
      const answerWords = answer.split(/\s+/).filter(w => w.length > 2)
      const sampleWords = sampleAnswer.split(/\s+/).filter(w => w.length > 2)
      
      if (answerWords.length >= 3) {
        const commonWords = answerWords.filter(word => sampleWords.some(sw => sw.includes(word) || word.includes(sw)))
        return commonWords.length > 0 || answerWords.length >= 5
      }
      return false
    } else {
      // Multiple choice and true/false - exact match
      return userAnswer === question.correct
    }
  }

  // Check if module completion criteria are met
  const checkModuleCompletion = (currentActivities: string[] = completedActivities, currentQuizScore: any = quizScore, currentShowResults: boolean = showQuizResults) => {
    if (isModuleCompleted) return // Already completed
    
    const criteria = module.completion_criteria
    const filesRead = currentActivities.filter(a => a.startsWith('Read')).length
    const activitiesCompleted = currentActivities.filter(a => !a.startsWith('Read')).length
    const quizCompleted = currentShowResults && currentQuizScore && currentQuizScore.percentage >= 70 // 70% minimum to pass
    
    const criteriaMet = {
      files: filesRead >= Math.min(criteria.read_files, module.resources.length),
      activities: activitiesCompleted >= criteria.activities_completed,
      quiz: module.quiz.length === 0 || quizCompleted // If no quiz, automatically pass
    }
    
    console.log('Module completion check:', {
      moduleId: module.id,
      criteriaMet,
      filesRead,
      activitiesCompleted,
      quizCompleted,
      isCompleted: isModuleCompleted
    })
    
    if (criteriaMet.files && criteriaMet.activities && criteriaMet.quiz) {
      setIsModuleCompleted(true)
      // Award module completion bonus and notify parent
      const moduleBonus = 200
      onComplete(moduleBonus)
      console.log('Module completed!', module.id)
    }
  }

  const completeActivity = (activityTitle: string, points: number) => {
    if (!completedActivities.includes(activityTitle)) {
      const newActivities = [...completedActivities, activityTitle]
      setCompletedActivities(newActivities)
      onComplete(points)
      // Check completion with updated activities immediately
      checkModuleCompletion(newActivities, quizScore, showQuizResults)
    }
  }

  const submitQuiz = () => {
    let correctCount = 0
    module.quiz.forEach((question, index) => {
      const userAnswer = quizAnswers[index]
      
      if (question.type === 'short_answer') {
        // For short answer questions, check if answer has reasonable content
        const answer = String(userAnswer || '').trim().toLowerCase()
        const sampleAnswer = String(question.sample_answer || '').trim().toLowerCase()
        
        // Basic scoring: if answer has at least 3 words and shares some key terms with sample
        const answerWords = answer.split(/\s+/).filter(w => w.length > 2)
        const sampleWords = sampleAnswer.split(/\s+/).filter(w => w.length > 2)
        
        if (answerWords.length >= 3) {
          // Check if answer contains some key concepts from sample answer
          const commonWords = answerWords.filter(word => sampleWords.some(sw => sw.includes(word) || word.includes(sw)))
          if (commonWords.length > 0 || answerWords.length >= 5) {
            correctCount++ // Give credit for reasonable effort
          }
        }
      } else {
        // Multiple choice and true/false - exact match
        if (userAnswer === question.correct) {
          correctCount++
        }
      }
    })
    
    const total = module.quiz.length
    const percentage = Math.round((correctCount / total) * 100)
    const basePoints = correctCount * 50
    const isPerfect = correctCount === total
    const newAttempts = quizAttempts + 1
    
    // Bonus points for perfect score and streaks
    let bonusPoints = 0
    let newStreak = perfectStreak
    
    if (isPerfect) {
      newStreak = perfectStreak + 1
      bonusPoints = newStreak * 25 // 25 bonus points per perfect streak
    } else {
      newStreak = 0
    }
    
    // First attempt bonus - only for the very first attempt
    if (newAttempts === 1 && percentage >= 80) {
      bonusPoints += 50
    }
    
    // For retries, only give base points (no bonus points to prevent farming)
    const totalPointsEarned = newAttempts === 1 ? basePoints + bonusPoints : basePoints
    
    const scoreData = {
      correct: correctCount,
      total,
      percentage,
      pointsEarned: totalPointsEarned,
      attempts: newAttempts,
      streak: newStreak
    }
    
    setQuizScore(scoreData)
    setQuizAttempts(newAttempts)
    setPerfectStreak(newStreak)
    setShowQuizResults(true)
    
    // Update global quiz stats
    updateQuizResult(module.id, percentage, newAttempts)
    
    // Only award points for first attempt, or if score improved significantly
    const shouldAwardPoints = newAttempts === 1 || (
      quizScore && percentage > quizScore.percentage + 20 // 20% improvement threshold
    )
    
    if (shouldAwardPoints) {
      onComplete(totalPointsEarned)
      console.log('Points awarded for quiz:', totalPointsEarned)
    } else {
      console.log('No points awarded for retry (prevent farming)')
    }
    
    // Check module completion after quiz with updated data
    checkModuleCompletion(completedActivities, scoreData, true)
  }

  const retryQuiz = () => {
    // Reset quiz state completely
    setQuizAnswers({})
    setShowQuizResults(false)
    setQuizScore(null)
    
    // Note: Don't reset quizAttempts as we want to track total attempts
    // Note: Don't reset isModuleCompleted as previous completion should stand
    
    console.log('Quiz retry initiated for module:', module.id)
  }

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600'
    if (percentage >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreEmoji = (percentage: number) => {
    if (percentage === 100) return '🏆'
    if (percentage >= 90) return '🌟'
    if (percentage >= 70) return '👍'
    return '📚'
  }

  const getDifficultyColor = (difficulty: string) => {
    const difficultyStr = String(difficulty || '').toLowerCase()
    switch (difficultyStr) {
      case 'beginner':
      case 'easy': return 'bg-green-100 text-green-800 border-green-300'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'advanced': return 'bg-red-100 text-red-800 border-red-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  if (!isUnlocked) {
    return (
      <div className="card opacity-50">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-bold text-gray-500">🔒 {module.title}</h4>
            <p className="text-sm text-gray-400">Complete previous modules to unlock</p>
          </div>
          <div className="text-2xl">🔒</div>
        </div>
      </div>
    )
  }

  if (isModuleCompleted) {
    return (
      <div className="card border-green-500 bg-green-50">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h4 className="text-lg font-bold text-green-800">✅ {module.title}</h4>
              <span className="px-2 py-1 text-xs bg-green-200 text-green-800 border border-green-400">
                Completed
              </span>
            </div>
            <p className="text-sm text-green-700">Great job! You&apos;ve mastered this module.</p>
          </div>
          <div className="text-2xl">🏆</div>
        </div>
        
        {/* Show completion summary */}
        <div className="mt-4 p-3 bg-white border border-green-300 rounded">
          <h5 className="font-medium text-sm mb-2">📋 Completion Summary</h5>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div>
              <span className="text-green-600">✅ Files Read:</span>
              <span className="ml-1">
                {completedActivities.filter(a => a.startsWith('Read')).length}/{Math.min(module.completion_criteria.read_files, module.resources.length)}
              </span>
            </div>
            <div>
              <span className="text-green-600">✅ Activities:</span>
              <span className="ml-1">
                {completedActivities.filter(a => !a.startsWith('Read')).length}/{module.completion_criteria.activities_completed}
              </span>
            </div>
            <div>
              <span className="text-green-600">✅ Quiz:</span>
              <span className="ml-1">
                {module.quiz.length === 0 ? 'N/A' : quizScore ? `${quizScore.percentage}%` : 'Pending'}
              </span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h4 className="text-lg font-bold">{module.title}</h4>
            <span className={`px-2 py-1 text-xs border-2 ${getDifficultyColor(module.difficulty)}`}>
              {module.difficulty}
            </span>
            <span className="text-xs text-gray-600">⏱️ {module.estimated_time}</span>
          </div>
          <p className="text-sm text-gray-600">{module.description}</p>
        </div>
        <div className="text-2xl">
          {isActive ? '📖' : '📚'}
        </div>
      </div>

      {isActive && (
        <div className="mt-6 space-y-6">
          {/* Learning Objectives */}
          <div>
            <h5 className="font-bold mb-2">🎯 Learning Objectives</h5>
            <ul className="text-sm space-y-1 list-none">
              {module.learning_objectives.map((objective, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span>•</span>
                  <span>{objective}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          {module.resources.length > 0 && (
            <div>
              <h5 className="font-bold mb-2">📁 Files to Explore</h5>
              <div className="grid gap-2">
                {module.resources.slice(0, 5).map((resource, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 border border-gray-200">
                    <span className="text-sm font-mono">{resource}</span>
                    <button 
                      onClick={() => completeActivity(`Read ${resource}`, 25)}
                      className="btn-secondary text-xs py-1 px-2"
                      disabled={completedActivities.includes(`Read ${resource}`)}
                    >
                      {completedActivities.includes(`Read ${resource}`) ? '✅' : 'Read'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Activities */}
          <div>
            <h5 className="font-bold mb-2">🎯 Activities</h5>
            <div className="space-y-3">
              {module.activities.map((activity, index) => (
                <div key={index} className="border-2 border-gray-200 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h6 className="font-medium">{activity.title}</h6>
                    <span className="text-xs bg-gray-100 px-2 py-1">
                      {activity.points} pts
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{activity.description}</p>
                  
                  <div className="text-xs space-y-1 mb-3">
                    <p className="font-medium">Instructions:</p>
                    {activity.instructions.map((instruction, i) => (
                      <p key={i} className="text-gray-600">• {instruction}</p>
                    ))}
                  </div>
                  
                  <button
                    onClick={() => completeActivity(activity.title, activity.points)}
                    className="btn-secondary text-xs py-1 px-3"
                    disabled={completedActivities.includes(activity.title)}
                  >
                    {completedActivities.includes(activity.title) ? '✅ Completed' : 'Mark Complete'}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Quiz */}
          {module.quiz.length > 0 && (
            <div>
              <h5 className="font-bold mb-2">❓ Knowledge Check</h5>
              <div className="space-y-4">
                {module.quiz.map((question, index) => (
                  <div key={index} className="border-2 border-gray-200 p-4">
                    <p className="font-medium mb-3">{question.question}</p>
                    
                    {question.type === 'multiple_choice' && question.options && (
                      <div className="space-y-2">
                        {question.options.map((option, optionIndex) => (
                          <label key={optionIndex} className="flex items-center space-x-2 cursor-pointer">
                            <input
                              type="radio"
                              name={`question-${index}`}
                              value={optionIndex}
                              checked={quizAnswers[index] === optionIndex}
                              onChange={(e) => setQuizAnswers(prev => ({ 
                                ...prev, 
                                [index]: parseInt(e.target.value) 
                              }))}
                              className="w-4 h-4"
                            />
                            <span className="text-sm">{option}</span>
                          </label>
                        ))}
                      </div>
                    )}
                    
                    {question.type === 'true_false' && (
                      <div className="space-y-2">
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            name={`question-${index}`}
                            value="true"
                            checked={quizAnswers[index] === true}
                            onChange={() => setQuizAnswers(prev => ({ ...prev, [index]: true }))}
                            className="w-4 h-4"
                          />
                          <span className="text-sm">True</span>
                        </label>
                        <label className="flex items-center space-x-2 cursor-pointer">
                          <input
                            type="radio"
                            name={`question-${index}`}
                            value="false"
                            checked={quizAnswers[index] === false}
                            onChange={() => setQuizAnswers(prev => ({ ...prev, [index]: false }))}
                            className="w-4 h-4"
                          />
                          <span className="text-sm">False</span>
                        </label>
                      </div>
                    )}
                    
                    {question.type === 'short_answer' && (
                      <div className="mt-3">
                        <textarea
                          placeholder="Type your answer here..."
                          value={quizAnswers[index] || ''}
                          onChange={(e) => setQuizAnswers(prev => ({ ...prev, [index]: e.target.value }))}
                          className="input-field w-full min-h-[80px] resize-vertical"
                          disabled={showQuizResults}
                        />
                        {showQuizResults && question.sample_answer && (
                          <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                            <p className="text-xs font-medium text-blue-800 mb-1">Sample Answer:</p>
                            <p className="text-xs text-blue-600">{question.sample_answer}</p>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {showQuizResults && (
                      <div className="mt-3 p-3 border-2 border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className={`text-xs font-medium ${
                            isQuestionCorrect(question, index) ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {isQuestionCorrect(question, index) ? '✅ Correct' : '❌ Incorrect'}
                          </span>
                          {!isQuestionCorrect(question, index) && question.type !== 'short_answer' && (
                            <span className="text-xs text-gray-500">
                              Correct: {question.type === 'multiple_choice' && question.options 
                                ? question.options[question.correct as number] 
                                : String(question.correct)}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-600">{question.explanation}</p>
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Quiz Results Display */}
                {showQuizResults && quizScore && (
                  <div className="mb-6 p-6 border-2 border-black bg-gray-50">
                    <div className="text-center mb-4">
                      <div className="text-4xl mb-2">{getScoreEmoji(quizScore.percentage)}</div>
                      <h4 className={`text-2xl font-bold mb-2 ${getScoreColor(quizScore.percentage)}`}>
                        {quizScore.percentage}% ({quizScore.correct}/{quizScore.total})
                      </h4>
                      <p className="text-sm text-gray-600 mb-4">
                        {quizScore.percentage === 100 ? 'Perfect Score! Amazing work!' :
                         quizScore.percentage >= 90 ? 'Excellent! You really understand this.' :
                         quizScore.percentage >= 70 ? 'Good job! You got most of it right.' :
                         'Keep learning! Review the explanations and try again.'}
                        {quizScore.attempts > 1 && (
                          <span className="block mt-1 text-xs text-blue-600">
                            💪 Retry #{quizScore.attempts - 1} - Keep improving!
                          </span>
                        )}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-center text-sm">
                      <div className="p-3 bg-white border border-black">
                        <div className="text-lg font-bold text-green-600">{quizScore.pointsEarned}</div>
                        <div className="text-xs text-gray-600">Points Earned</div>
                      </div>
                      <div className="p-3 bg-white border border-black">
                        <div className="text-lg font-bold">{quizScore.attempts}</div>
                        <div className="text-xs text-gray-600">Attempt{quizScore.attempts !== 1 ? 's' : ''}</div>
                      </div>
                      <div className="p-3 bg-white border border-black">
                        <div className="text-lg font-bold text-purple-600">{quizScore.streak}</div>
                        <div className="text-xs text-gray-600">Perfect Streak</div>
                      </div>
                      <div className="p-3 bg-white border border-black">
                        <div className="text-lg font-bold text-blue-600">
                          {quizScore.attempts === 1 && quizScore.percentage >= 80 ? '+50' : '0'}
                        </div>
                        <div className="text-xs text-gray-600">First Try Bonus</div>
                      </div>
                    </div>

                    {/* Performance Analytics */}
                    <div className="mb-4">
                      <h5 className="font-medium text-sm mb-2">📊 Performance Breakdown</h5>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>Base Points ({quizScore.correct} × 50):</span>
                          <span className="font-medium">{quizScore.correct * 50}</span>
                        </div>
                        {quizScore.streak > 0 && (
                          <div className="flex justify-between text-xs text-purple-600">
                            <span>Perfect Streak Bonus ({quizScore.streak} × 25):</span>
                            <span className="font-medium">+{quizScore.streak * 25}</span>
                          </div>
                        )}
                        {quizScore.attempts === 1 && quizScore.percentage >= 80 && (
                          <div className="flex justify-between text-xs text-blue-600">
                            <span>First Attempt Bonus:</span>
                            <span className="font-medium">+50</span>
                          </div>
                        )}
                        <div className="border-t pt-2 flex justify-between font-medium text-sm">
                          <span>Total Points:</span>
                          <span className="text-green-600">{quizScore.pointsEarned}</span>
                        </div>
                      </div>
                    </div>

                    {/* Achievement Notifications */}
                    {quizScore.percentage === 100 && quizScore.attempts === 1 && (
                      <div className="mb-4 p-3 bg-yellow-50 border-2 border-yellow-300">
                        <p className="text-sm font-medium text-yellow-800">
                          🏆 Achievement Unlocked: "Quiz Master" - Perfect score on first try!
                        </p>
                      </div>
                    )}
                    
                    {quizScore.streak >= 3 && (
                      <div className="mb-4 p-3 bg-purple-50 border-2 border-purple-300">
                        <p className="text-sm font-medium text-purple-800">
                          🔥 Achievement Unlocked: "Streak Master" - {quizScore.streak} perfect quizzes in a row!
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Submit/Retry Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={submitQuiz}
                    className="btn-primary flex-1"
                    disabled={showQuizResults || Object.keys(quizAnswers).length !== module.quiz.length}
                  >
                    {showQuizResults ? '✅ Submitted' : 'Submit Quiz'}
                  </button>
                  
                  {showQuizResults && (
                    <button
                      onClick={retryQuiz}
                      className="btn-secondary"
                      title="Retake the quiz to improve your understanding"
                    >
                      🔄 Retry Quiz
                      {quizScore && quizScore.percentage < 100 && (
                        <span className="text-xs block">Try for 100%!</span>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Progress */}
          <div className="bg-gray-50 p-4 border-2 border-gray-200">
            <h6 className="font-medium mb-2">📊 Module Progress</h6>
            
            {/* Progress calculation */}
            {(() => {
              const criteria = module.completion_criteria
              const filesRead = completedActivities.filter(a => a.startsWith('Read')).length
              const activitiesCompleted = completedActivities.filter(a => !a.startsWith('Read')).length
              const quizCompleted = showQuizResults && quizScore && quizScore.percentage >= 70
              
              const maxFiles = Math.min(criteria.read_files, module.resources.length)
              const fileProgress = maxFiles > 0 ? (filesRead / maxFiles) * 100 : 100
              const activityProgress = criteria.activities_completed > 0 ? (activitiesCompleted / criteria.activities_completed) * 100 : 100
              const quizProgress = module.quiz.length === 0 ? 100 : (quizCompleted ? 100 : 0)
              
              const overallProgress = (fileProgress + activityProgress + quizProgress) / 3
              
              return (
                <>
                  <div className="mb-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span>Overall Progress</span>
                      <span>{Math.round(overallProgress)}%</span>
                    </div>
                    <div className="progress-bar h-2">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${overallProgress}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="text-xs space-y-1">
                    <div className="flex justify-between">
                      <span>Files Read:</span>
                      <span className={filesRead >= maxFiles ? 'text-green-600 font-medium' : ''}>
                        {filesRead} / {maxFiles}
                        {filesRead >= maxFiles && ' ✅'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Activities:</span>
                      <span className={activitiesCompleted >= criteria.activities_completed ? 'text-green-600 font-medium' : ''}>
                        {activitiesCompleted} / {criteria.activities_completed}
                        {activitiesCompleted >= criteria.activities_completed && ' ✅'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Quiz:</span>
                      <span className={quizCompleted ? 'text-green-600 font-medium' : ''}>
                        {module.quiz.length === 0 ? 'N/A ✅' : 
                         showQuizResults ? `${quizScore?.percentage}%${quizCompleted ? ' ✅' : ' ❌'}` : '⏳ Pending'}
                      </span>
                    </div>
                  </div>
                  
                  {overallProgress === 100 && !isModuleCompleted && (
                    <div className="mt-3 p-2 bg-yellow-50 border border-yellow-300 rounded">
                      <p className="text-xs text-yellow-800 font-medium">
                        🎉 Ready to complete! All criteria met.
                      </p>
                    </div>
                  )}
                </>
              )
            })()}
          </div>
        </div>
      )}
    </div>
  )
}