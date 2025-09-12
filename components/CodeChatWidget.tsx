'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Loader2 } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Array<{
    file_path: string
    lines: string
    language: string
    similarity_score: number
  }>
}

interface CodeChatWidgetProps {
  repoName: string | null
  isVisible?: boolean
}

export default function CodeChatWidget({ repoName, isVisible = true }: CodeChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(true)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize with welcome message when repo is available
  useEffect(() => {
    if (repoName && messages.length === 0) {
      setMessages([{
        id: '1',
        type: 'assistant',
        content: `Hi! I'm your AI code assistant. I can help you understand the "${repoName}" repository. Ask me questions about the code structure, specific functions, design patterns, or anything else!`,
        timestamp: new Date()
      }])
    }
  }, [repoName, messages.length])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!inputValue.trim() || !repoName || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          repo_name: repoName,
          user_level: 'intermediate'
        })
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.success ? data.answer : `Sorry, I encountered an error: ${data.error}`,
        timestamp: new Date(),
        sources: data.sources || []
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant', 
        content: 'Sorry, I encountered a technical error. Please try again later.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  if (!isVisible || !repoName) return null

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Widget */}
      {isOpen && (
        <div className="mb-4 w-80 h-96 bg-white border-2 border-black shadow-lg rounded-lg flex flex-col max-w-[90vw] max-h-[90vh]">
          {/* Header */}
          <div className="bg-black text-white p-3 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <MessageCircle size={16} className="flex-shrink-0" />
              <span className="font-medium text-sm truncate">Ask about {repoName}</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-gray-700 p-1 rounded flex-shrink-0 ml-2"
            >
              <X size={16} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-lg text-sm break-words overflow-hidden ${
                    message.type === 'user'
                      ? 'bg-black text-white'
                      : 'bg-gray-100 text-black border'
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words overflow-wrap-anywhere leading-relaxed">
                    {message.content}
                  </p>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      <p className="text-xs font-medium mb-1">Sources:</p>
                      {message.sources.slice(0, 3).map((source, idx) => (
                        <div key={idx} className="text-xs text-gray-600 mb-1 break-all">
                          <span className="font-mono text-xs">{source.file_path}</span>
                          {source.lines && <span className="ml-1">(lines {source.lines})</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 border p-2 rounded-lg">
                  <Loader2 size={16} className="animate-spin" />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-3 border-t flex-shrink-0">
            <div className="flex gap-2 items-end">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about the code..."
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-black min-w-0"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className="px-3 py-2 bg-black text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
              >
                <Send size={16} />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-black text-white rounded-full shadow-lg hover:bg-gray-800 transition-colors flex items-center justify-center"
      >
        {isOpen ? <X size={20} /> : <MessageCircle size={20} />}
      </button>
    </div>
  )
}