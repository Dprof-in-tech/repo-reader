'use client'

import { useState } from 'react'
import RepositoryAnalyzer from '@/components/RepositoryAnalyzer'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-6xl font-bold mb-4 text-shadow">
              REPO READER
            </h1>
            <p className="text-lg md:text-xl mb-2 font-medium">
              AI-powered repository analysis and gamified code walkthroughs
            </p>
            <p className="text-sm text-gray-600 mb-8">
              Enter a GitHub repository URL and get an interactive learning experience
            </p>
          </div>
          
          <RepositoryAnalyzer />
          
          <div className="mt-16 grid md:grid-cols-3 gap-8">
            <div className="card card-hover">
              <h3 className="text-xl font-bold mb-3">🔍 Smart Analysis</h3>
              <p className="text-sm">
                Automatically detects architecture patterns, frameworks, and code complexity
              </p>
            </div>
            <div className="card card-hover">
              <h3 className="text-xl font-bold mb-3">🎮 Gamified Learning</h3>
              <p className="text-sm">
                Achievements, progress tracking, and interactive modules make learning fun
              </p>
            </div>
            <div className="card card-hover">
              <h3 className="text-xl font-bold mb-3">⚡ Quick Start</h3>
              <p className="text-sm">
                Just paste a GitHub URL and get a structured walkthrough in minutes
              </p>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
