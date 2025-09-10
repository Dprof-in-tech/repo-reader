import Link from 'next/link'

export default function Header() {
  return (
    <header className="border-b-2 border-black bg-white">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold hover:text-gray-600 transition-colors">
            REPO READER
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link 
              href="/demo" 
              className="font-medium hover:text-gray-600 transition-colors"
            >
              Demo
            </Link>
            <Link 
              href="/about" 
              className="font-medium hover:text-gray-600 transition-colors"
            >
              About
            </Link>
            <a 
              href="https://github.com/your-username/repo-reader" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-secondary text-sm py-2 px-4"
            >
              GitHub
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}