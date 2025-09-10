# 🎮 Repo Reader - AI-Powered Repository Analysis & Gamified Learning

<p align="center">
  <img src="https://via.placeholder.com/150x150/000000/FFFFFF?text=RR" alt="Repo Reader Logo" width="150" height="150">
</p>

<p align="center">
  Transform any GitHub repository into an interactive, gamified learning experience with AI-powered analysis and intelligent code walkthroughs.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#local-setup">Local Setup</a> •
  <a href="#ai-models">AI Models</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a>
</p>

## 🚀 What is Repo Reader?

Repo Reader is an intelligent repository analysis tool that uses AI to create engaging, gamified walkthroughs of any GitHub repository. It transforms complex codebases into structured learning experiences with:

- **🤖 AI-Powered Analysis**: Deep code understanding using advanced language models
- **🎯 Gamified Learning**: Progress tracking, achievements, and interactive quizzes  
- **📚 Smart Documentation**: Auto-generated explanations and learning paths
- **🔍 Intelligent Code Exploration**: Contextual file analysis and architecture insights
- **⚡ Hybrid AI Models**: Support for both local (GPT OSS 20B) and cloud (OpenAI) models

## ✨ Features

### 🎯 Core Functionality
- **Repository Analysis**: Clones and analyzes GitHub repositories automatically
- **Code Structure Detection**: Identifies frameworks, languages, and architectural patterns
- **Learning Path Generation**: Creates progressive, difficulty-appropriate walkthroughs
- **Interactive Quizzes**: Codebase-specific questions that test real understanding
- **Progress Tracking**: Gamified experience with points, levels, and achievements

### 🤖 AI-Powered Intelligence
- **Hybrid LLM Support**: Local GPT OSS 20B model with OpenAI fallback
- **Context-Aware Analysis**: Understanding of project structure and dependencies
- **Smart Quiz Generation**: Three-tier system (LLM → Codebase Analysis → Generic)
- **Code Quality Assessment**: Documentation scores, complexity analysis
- **Architecture Pattern Recognition**: Automatic detection of common patterns

### 🎮 Gamification Elements
- **Achievement System**: Unlock badges for learning milestones
- **Progress Visualization**: Interactive progress bars and completion tracking
- **Level System**: Advance through difficulty levels as you learn
- **Social Features**: Share progress and achievements
- **Completion Certificates**: Earn recognition for completed walkthroughs

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.13+ 
- Git
- OpenAI API key (optional: for cloud AI features)

### 1. Clone and Install
```bash
git clone <repository-url>
cd repo-reader
npm install  # or pnpm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys (at minimum, add OPENAI_API_KEY)
```

### 3. Install Python Dependencies
```bash
cd api
pip install -r requirements.txt
cd ..
```

### 4. Start Development Servers
```bash
npm run dev
```

This starts:
- **Frontend**: http://localhost:3000 (Next.js)
- **API**: http://localhost:5328 (Flask)

### 5. Try It Out!
1. Open http://localhost:3000
2. Enter a GitHub repository URL
3. Select your experience level (Beginner/Intermediate/Advanced)
4. Watch the AI analyze the repository and create your personalized walkthrough!

## 🛠 Local Setup

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Local Model Support
CHATGPT_OSS_MODEL_PATH=openai/gpt-oss-20b
LOCAL_MODEL_PREFER=true

# Optional: LangSmith for Debugging
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=repo-reader-project
```

### Development Commands

```bash
# Start both frontend and backend
npm run dev

# Start only frontend
npm run next-dev

# Start only backend  
npm run flask-dev

# Build for production
npm run build
```

## 🤖 AI Models

### Supported Models

#### 1. OpenAI GPT Models (Cloud)
- **Model**: GPT-4 / GPT-3.5-turbo
- **Use Case**: Primary analysis and quiz generation
- **Pros**: High quality, fast, reliable
- **Cons**: Requires API key, costs money

#### 2. GPT OSS 20B (Local)
- **Model**: OpenAI's open-source GPT model
- **Use Case**: Privacy-focused local analysis
- **Pros**: Free, private, offline capable
- **Cons**: Requires powerful hardware

### Local Model Setup

#### Quick Setup (Recommended)
```bash
# Uses HuggingFace Hub - no download needed
echo 'CHATGPT_OSS_MODEL_PATH=openai/gpt-oss-20b' >> .env
echo 'LOCAL_MODEL_PREFER=true' >> .env
```

#### Advanced Setup
```bash
# Download model locally (~40GB)
pip install -U huggingface_hub
huggingface-cli download openai/gpt-oss-20b --local-dir ./models/gpt-oss-20b/
```

#### Hardware Requirements

**Minimum**:
- 16GB RAM
- 15GB storage
- Modern CPU

**Recommended**:
- NVIDIA RTX 3080+ (12GB+ VRAM)
- 32GB RAM  
- SSD with 25GB+ space
- 8+ core CPU

#### Performance Tuning

For **CPU-only** systems:
```env
LOCAL_MODEL_GPU_LAYERS=0
LOCAL_MODEL_THREADS=8
LOCAL_MODEL_BATCH_SIZE=256
```

For **GPU-accelerated** systems:
```env
LOCAL_MODEL_GPU_LAYERS=35
LOCAL_MODEL_THREADS=4
LOCAL_MODEL_BATCH_SIZE=512
```

### Model Selection Priority

The system automatically chooses models in this order:
1. **Local GPT OSS 20B** (if available and `LOCAL_MODEL_PREFER=true`)
2. **OpenAI GPT models** (cloud fallback)
3. **Static generation** (if both fail)

## 🏗 Architecture

### Tech Stack
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: Flask, Python 3.13
- **AI/ML**: LangChain, LangGraph, OpenAI, HuggingFace Transformers
- **Database**: File-based storage (JSON)
- **Deployment**: Vercel (Frontend), Vercel Functions (Backend)

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js App  │───▶│   Flask API      │───▶│  LangGraph     │
│   (Frontend)    │    │   (Backend)      │    │  Agent         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  GitHub API      │    │ AI Models       │
                       │  (Repo Cloning)  │    │ (Analysis)      │
                       └──────────────────┘    └─────────────────┘
```

### Core Components

#### 🤖 LangGraph Agent (`api/agent.py`)
- Orchestrates the entire analysis workflow
- Manages state between analysis steps
- Handles streaming progress updates

#### 🛠 Analysis Tools (`api/tools/`)
- **RepoReaderTool**: Clones and extracts repository data  
- **CodeAnalyzerTool**: Performs static and AI-powered code analysis
- **WalkthroughGeneratorTool**: Creates gamified learning experiences
- **CodebaseQuizGenerator**: Generates intelligent, code-specific quizzes

#### 🧠 Hybrid LLM Manager (`api/llm_manager.py`)
- Manages local and cloud AI models
- Automatic fallback between model types
- Performance optimization and caching

#### 🎮 Frontend Components (`components/`)
- **WalkthroughDisplay**: Main learning interface
- **LearningModule**: Individual lesson components  
- **ProgressTracker**: Gamification elements
- **QuizComponents**: Interactive question interfaces

## 🎯 Usage Examples

### Basic Analysis
```typescript
import { analyzeRepository } from '@/lib/api'

const result = await analyzeRepository(
  'https://github.com/user/repo',
  'intermediate'
)

console.log(result.walkthrough_data.learning_modules)
```

### Streaming Analysis
```typescript
import { analyzeRepositoryStreaming } from '@/lib/api'

const result = await analyzeRepositoryStreaming(
  'https://github.com/user/repo',
  'beginner',
  (progress) => {
    console.log('Progress:', progress.content)
  }
)
```

### Local Model Testing
```bash
curl -X POST http://localhost:5328/api/llm-test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze this code structure", "prefer_local": true}'
```

## 🚀 Deployment

### Vercel Deployment (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone)

1. Connect your GitHub repository
2. Set environment variables in Vercel dashboard
3. Deploy automatically

### Manual Deployment

```bash
# Build the application
npm run build

# Deploy frontend
vercel --prod

# Backend automatically deploys as Vercel Functions
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Use TypeScript for frontend code
- Follow Python PEP 8 for backend code
- Add JSDoc/docstring comments for public functions
- Use descriptive commit messages

### Testing
```bash
# Run frontend tests
npm test

# Run backend tests  
cd api && python -m pytest

# Type checking
npm run type-check
```

## 🐛 Troubleshooting

### Common Issues

**Flask server won't start:**
```bash
cd api
pip install -r requirements.txt
python index.py
```

**Local model fails to load:**
- Check available RAM/VRAM
- Reduce `LOCAL_MODEL_GPU_LAYERS` if using GPU
- Try CPU-only mode: `LOCAL_MODEL_GPU_LAYERS=0`

**OpenAI API errors:**
- Verify `OPENAI_API_KEY` is set correctly
- Check API usage limits
- Ensure sufficient account balance

**Repository cloning fails:**
- Check internet connection
- Verify repository is public
- Try a smaller repository first

### Performance Tips
- Use SSD storage for better I/O performance
- Enable GPU acceleration if available  
- Adjust batch sizes based on available memory
- Use local models for privacy and cost savings

## 📊 Monitoring

Check system status:
```bash
# LLM model status
curl http://localhost:5328/api/llm-status

# Agent workflow status  
curl http://localhost:5328/api/status

# Health check
curl http://localhost:5328/api/health
```

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain & LangGraph**: For the AI orchestration framework
- **OpenAI**: For GPT models and API
- **HuggingFace**: For open-source model hosting
- **Vercel**: For hosting and deployment platform
- **Next.js & Flask**: For the full-stack framework

---

<p align="center">
  Made with ❤️ for developers who want to understand code better
</p>

<p align="center">
  <a href="https://github.com/your-username/repo-reader/issues">Report Bug</a> •
  <a href="https://github.com/your-username/repo-reader/issues">Request Feature</a> •
  <a href="https://github.com/your-username/repo-reader/discussions">Discussions</a>
</p>