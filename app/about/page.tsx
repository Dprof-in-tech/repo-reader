import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-3xl md:text-5xl font-bold mb-4 text-shadow">
              ABOUT REPO READER
            </h1>
            <p className="text-lg font-medium text-gray-600">
              AI-powered repository analysis and gamified learning
            </p>
          </div>

          <div className="space-y-8">
            <div className="card">
              <h2 className="text-2xl font-bold mb-4">🎯 What is Repo Reader?</h2>
              <p className="mb-4">
                Repo Reader is an AI-powered tool that analyzes GitHub repositories and generates 
                interactive, gamified walkthroughs to help developers understand codebases more effectively.
              </p>
              <p>
                Whether you&apos;re joining a new team, exploring open source projects, or learning from 
                existing codebases, Repo Reader transforms the overwhelming task of code exploration 
                into an engaging, structured learning experience.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card">
                <h3 className="text-xl font-bold mb-3">🔍 Smart Analysis</h3>
                <ul className="space-y-2 text-sm list-none">
                  <li>• Automatic architecture pattern detection</li>
                  <li>• Code complexity scoring</li>
                  <li>• Framework and language identification</li>
                  <li>• Entry point discovery</li>
                  <li>• Dependency mapping</li>
                </ul>
              </div>

              <div className="card">
                <h3 className="text-xl font-bold mb-3">🎮 Gamified Learning</h3>
                <ul className="space-y-2 text-sm list-none">
                  <li>• Achievement system with badges</li>
                  <li>• Progress tracking and levels</li>
                  <li>• Interactive quizzes and activities</li>
                  <li>• Structured learning modules</li>
                  <li>• Personalized difficulty scaling</li>
                </ul>
              </div>
            </div>

            <div className="card">
              <h2 className="text-2xl font-bold mb-4">🛠️ Technology Stack</h2>
              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-bold mb-2">AI & Backend</h4>
                  <ul className="text-sm space-y-1 list-none">
                    <li>• LangGraph for AI orchestration</li>
                    <li>• LangChain for tool management</li>
                    <li>• OpenAI GPT for analysis</li>
                    <li>• Flask API server</li>
                    <li>• Python for processing</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-bold mb-2">Frontend</h4>
                  <ul className="text-sm space-y-1 list-none">
                    <li>• Next.js 13+ with App Router</li>
                    <li>• React with TypeScript</li>
                    <li>• Tailwind CSS for styling</li>
                    <li>• Responsive design</li>
                    <li>• Progressive Web App ready</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-bold mb-2">Features</h4>
                  <ul className="text-sm space-y-1 list-none">
                    <li>• Real-time progress tracking</li>
                    <li>• Interactive code exploration</li>
                    <li>• Syntax highlighting</li>
                    <li>• Mobile-friendly interface</li>
                    <li>• Accessibility optimized</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="card">
              <h2 className="text-2xl font-bold mb-4">🚀 How It Works</h2>
              <div className="grid md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-3xl mb-2">📂</div>
                  <h4 className="font-bold mb-1">1. Submit URL</h4>
                  <p className="text-xs text-gray-600">
                    Enter any public GitHub repository URL
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl mb-2">🔍</div>
                  <h4 className="font-bold mb-1">2. AI Analysis</h4>
                  <p className="text-xs text-gray-600">
                    LangGraph agent analyzes code structure
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl mb-2">🎮</div>
                  <h4 className="font-bold mb-1">3. Generate Quest</h4>
                  <p className="text-xs text-gray-600">
                    Creates gamified learning modules
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl mb-2">📚</div>
                  <h4 className="font-bold mb-1">4. Learn & Explore</h4>
                  <p className="text-xs text-gray-600">
                    Interactive walkthrough with achievements
                  </p>
                </div>
              </div>
            </div>

            <div className="card bg-gray-50">
              <h2 className="text-2xl font-bold mb-4">🎯 Perfect For</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-bold mb-2">👨‍💻 Developers</h4>
                  <ul className="text-sm space-y-1 list-none">
                    <li>• Onboarding to new codebases</li>
                    <li>• Understanding open source projects</li>
                    <li>• Learning new frameworks and patterns</li>
                    <li>• Code review preparation</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-bold mb-2">🎓 Students & Teams</h4>
                  <ul className="text-sm space-y-1 list-none">
                    <li>• Computer science education</li>
                    <li>• Team knowledge sharing</li>
                    <li>• Architecture documentation</li>
                    <li>• Best practices learning</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}