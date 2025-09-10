'use client'

import { useState, useEffect, useRef } from 'react'
import { ProgressMessage } from '@/lib/api'

interface StreamingProgressProps {
  messages: ProgressMessage[]
  isActive: boolean
}

export default function StreamingProgress({ messages, isActive }: StreamingProgressProps) {
  const [visibleMessages, setVisibleMessages] = useState<ProgressMessage[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    // Animate new messages appearing
    const timeout = setTimeout(() => {
      setVisibleMessages(messages)
    }, 50)
    
    return () => clearTimeout(timeout)
  }, [messages])
  
  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [visibleMessages])

  if (!isActive && messages.length === 0) return null

  const getMessageIcon = (content: string) => {
    if (content.includes('🚀') || content.includes('Starting')) return '🚀'
    if (content.includes('📁') || content.includes('Cloning')) return '📁'
    if (content.includes('📦') || content.includes('Receiving') || content.includes('remote:')) return '📦'
    if (content.includes('🔗') || content.includes('Resolving')) return '🔗'
    if (content.includes('⬇️') || content.includes('%')) return '⬇️'
    if (content.includes('✅') || content.includes('success')) return '✅'
    if (content.includes('🔍') || content.includes('Analyzing')) return '🔍'
    if (content.includes('📊') || content.includes('complete')) return '📊'
    if (content.includes('❌') || content.includes('Error') || content.includes('failed')) return '❌'
    return 'ℹ️'
  }

  const getMessageStyle = (content: string) => {
    if (content.includes('❌') || content.includes('Error') || content.includes('failed')) {
      return 'text-red-600 bg-red-50 border-red-200'
    }
    if (content.includes('✅') || content.includes('success') || content.includes('complete')) {
      return 'text-green-600 bg-green-50 border-green-200'
    }
    if (content.includes('%') && content.includes('Receiving')) {
      return 'text-blue-600 bg-blue-50 border-blue-200'
    }
    return 'text-gray-700 bg-gray-50 border-gray-200'
  }

  return (
    <div className="card mb-8">
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
        <h3 className="text-lg font-semibold">
          {isActive ? 'Repository Analysis in Progress' : 'Analysis Complete'}
        </h3>
      </div>
      
      <div className="bg-black rounded-lg p-4 font-mono text-sm max-h-80 overflow-y-auto">
        <div className="space-y-1">
          {visibleMessages.map((message, index) => (
            <div 
              key={index}
              className={`flex items-start gap-2 p-2 rounded border transition-all duration-50 ${getMessageStyle(message.content)}`}
              style={{
                animation: `fadeInUp 0.01s ease-out ${index * 0.01}s both`
              }}
              ref={messagesEndRef}
            >
              <span className="text-lg flex-shrink-0">
                {getMessageIcon(message.content)}
              </span>
              <span className="flex-1 break-all">
                {message.content.replace(/^[🚀📁📦🔗⬇️✅🔍📊❌ℹ️]\s*/, '')}
              </span>
              <span className="text-xs opacity-60 flex-shrink-0">
                {new Date(message.timestamp * 1000).toLocaleTimeString()}
              </span>
            </div>
          ))}
          
          {isActive && (
            <div className="flex items-center gap-2 p-2 text-blue-600 bg-blue-50 border border-blue-200 rounded">
              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          )}
        </div>
      </div>
      
      {!isActive && messages.length > 0 && (
        <div className="mt-4 text-center">
          <div className="inline-flex items-center gap-2 text-green-600 bg-green-50 px-4 py-2 rounded-lg">
            <span className="text-lg">🎉</span>
            <span className="font-medium">Analysis completed successfully!</span>
          </div>
        </div>
      )}
    </div>
  )
}