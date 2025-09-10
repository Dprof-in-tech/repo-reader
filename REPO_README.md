# 🎮 Repo Reader

AI-powered repository analysis and gamified code walkthroughs using LangGraph.

![Repo Reader Demo](https://via.placeholder.com/800x400/000000/FFFFFF?text=REPO+READER)

## ✨ Features

- 🔍 **Smart Repository Analysis** - Automatic detection of architecture patterns, frameworks, and complexity
- 🎮 **Gamified Learning** - Achievement systems, progress tracking, and interactive modules  
- 📊 **Code Quality Assessment** - Complexity scoring, organization analysis, and best practices
- 🏆 **Progress Tracking** - Levels, achievements, and completion tracking
- ⚡ **Fast Analysis** - Powered by LangGraph for efficient AI orchestration
- 📱 **Responsive Design** - Works perfectly on desktop and mobile

## 🛠️ Tech Stack

### Backend
- **LangGraph** - AI agent orchestration framework
- **LangChain** - Tool management and LLM integration  
- **Flask** - REST API server
- **OpenAI GPT** - Code analysis and walkthrough generation
- **Python 3.8+** - Core processing

### Frontend  
- **Next.js 13+** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Responsive Design** - Mobile-first approach

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 16+** with npm
3. **Git** for repository cloning
4. **OpenAI API Key** for AI analysis

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd repo-reader
   ```

2. **Set up environment**
   ```bash
   # Create and activate Python virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   npm install
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

4. **Start development servers**
   ```bash
   # Option 1: Use the convenient start script
   ./start-dev.sh
   
   # Option 2: Start manually
   # Terminal 1 - Flask API
   cd api && python index.py
   
   # Terminal 2 - Next.js Frontend  
   npm run next-dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:5328
   - API Status: http://localhost:5328/api/status

## 📖 Usage

### Analyze a Repository

1. **Visit the homepage** at http://localhost:3000
2. **Enter a GitHub URL** (e.g., `https://github.com/microsoft/vscode`)
3. **Select your experience level** (Beginner, Intermediate, Advanced)
4. **Click "Analyze Repository"** and wait for the AI analysis
5. **Explore the generated walkthrough** with interactive modules and achievements

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/status` - Agent capabilities and workflow info  
- `GET /api/demo` - Sample walkthrough data
- `POST /api/analyze` - Analyze repository (requires `github_url` and `user_level`)

### Example API Request

```bash
curl -X POST http://localhost:5328/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/microsoft/vscode",
    "user_level": "intermediate"
  }'
```

## 🎯 How It Works

### LangGraph AI Agent Workflow

```
GitHub URL → Repository Reader → Code Analyzer → Walkthrough Generator → Gamified Output
```

1. **Repository Reader Tool** - Clones GitHub repo and extracts file structure
2. **Code Analyzer Tool** - Detects patterns, complexity, and architecture  
3. **Walkthrough Generator Tool** - Creates gamified learning modules with quizzes
4. **LangGraph Orchestrator** - Coordinates the entire analysis workflow

### Gamification Elements

- 🏆 **Achievements** - Code Detective, Architecture Master, Framework Expert
- 📈 **Progress Levels** - From Code Newbie to Code Wizard  
- 🎯 **Interactive Activities** - File exploration, pattern recognition, code tracing
- 📝 **Knowledge Quizzes** - Multiple choice and true/false questions
- ⭐ **Difficulty Scaling** - Adaptive content based on user experience

## 📁 Project Structure

```
repo-reader/
├── api/                    # Flask backend
│   ├── tools/             # LangGraph tools
│   │   ├── repo_reader.py
│   │   ├── code_analyzer.py
│   │   └── walkthrough_generator.py
│   ├── agent.py           # Main LangGraph agent
│   └── index.py           # Flask app
├── app/                   # Next.js frontend
│   ├── demo/              # Demo page
│   ├── about/             # About page
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Homepage
├── components/            # React components
│   ├── RepositoryAnalyzer.tsx
│   ├── WalkthroughDisplay.tsx
│   ├── LearningModule.tsx
│   └── ...
├── lib/                   # Utilities
│   └── api.ts             # API client
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
└── start-dev.sh          # Development startup script
```

## 🎨 Design Philosophy

### Minimal Black & White Theme
- **High contrast** for maximum readability
- **Brutalist shadows** for depth and emphasis  
- **Monospace fonts** for code-focused aesthetic
- **Clean typography** with clear hierarchy
- **Interactive elements** with hover states and animations

### Best Practices
- **Component-based architecture** with reusable UI elements
- **TypeScript** for type safety and better DX
- **Responsive design** with mobile-first approach
- **Accessibility** optimized with ARIA labels and keyboard navigation
- **Performance** optimized with code splitting and lazy loading

## 🧪 Testing

```bash
# Test Flask API
curl http://localhost:5328/api/health

# Test demo endpoint  
curl http://localhost:5328/api/demo

# Build frontend (checks for errors)
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🚧 Development

### Adding New Tools

1. Create tool in `api/tools/your_tool.py`
2. Inherit from `BaseTool` with proper type annotations  
3. Add to agent in `api/agent.py`
4. Update workflow graph if needed

### Frontend Components

- Follow the established component pattern
- Use TypeScript for all components
- Implement proper error boundaries
- Add loading states for async operations
- Follow the black & white design system

## 📈 Roadmap

- [ ] **Authentication** - User accounts and saved walkthroughs
- [ ] **Private Repository Support** - GitHub token integration
- [ ] **Team Collaboration** - Shared walkthroughs and progress
- [ ] **Advanced Analytics** - Detailed code metrics and insights
- [ ] **Export Features** - PDF/Markdown walkthrough exports
- [ ] **Plugin System** - Custom analysis tools and generators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph** team for the excellent AI orchestration framework
- **LangChain** community for tool management patterns
- **Next.js** team for the amazing React framework
- **Tailwind CSS** for the utility-first styling approach

---

Built with ❤️ for developers who want to understand code better.