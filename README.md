# Autonomous AI Agent System

A fully autonomous, locally-run AI agent system capable of end-to-end execution of extremely complex tasks—from enterprise-grade applications to advanced quantitative trading strategies. Built with Electron, React, FastAPI, and powered by local Ollama models.

## 🚀 Core Capabilities

### Multi-Agent Orchestration
- **Planner Agent** (codellama:instruct): Breaks objectives into ordered subtasks and coordinates execution
- **Designer Agent** (codellama:instruct): Creates specifications, architectures, and strategic designs  
- **Coder Agent** (deepseek-coder): Implements code, tests, and configurations
- **Context Agent**: Maintains comprehensive system memory and awareness

### Enterprise Development Pipeline
- **Full-Stack App Scaffolding**: React, Python, Node.js, Go projects with complete CI/CD
- **Git Integration**: Automated version control, commits, and deployments
- **Docker Operations**: Build, run, and orchestrate containerized applications
- **Cloud Deployment**: Local development with production-ready configurations

### Quantitative Trading System
- **Strategy Development**: Bollinger Bands, Momentum, and custom strategies
- **Backtesting Engine**: Historical performance analysis with risk metrics
- **Risk Management**: Portfolio optimization, stop-loss, position sizing
- **Performance Analytics**: Sharpe ratio, drawdown, profit factor calculations

### System Automation & Memory
- **OS-Level Control**: Screenshot analysis, mouse/keyboard automation, clipboard operations
- **Persistent Context**: ChromaDB vector database for cross-session memory
- **Filesystem Monitoring**: Real-time project and development tracking
- **Command History**: Complete audit trail of all system interactions

## 📋 Prerequisites

### Required Software
```bash
# 1. Node.js (v16+)
node --version

# 2. Python 3.11+
python3 --version

# 3. Ollama with required models
ollama pull codellama:instruct
ollama pull deepseek-coder
ollama list

# 4. System dependencies
brew install tesseract        # macOS
sudo apt install tesseract    # Ubuntu
```

### Optional Enhancements
```bash
# Docker for containerization
docker --version

# Git for version control
git --version

# VSCode for IDE integration
code --version
```

## ⚡ Quick Start

### 1. Installation
```bash
# Clone and setup
git clone <repository-url>
cd autonomous-ai-agent
npm install

# Setup Python backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Configuration
```bash
# Backend configuration (backend/.env)
OLLAMA_URL=http://localhost:11434
CONTROL_MODEL=codellama:instruct
CODE_MODEL=deepseek-coder

# Frontend configuration (.env.local) 
VITE_BACKEND_URL=http://127.0.0.1:8001/v1
VITE_APP_NAME=Autonomous AI Agent System
```

### 3. Launch System
```bash
# Start all services
npm start

# Or start individually:
# Terminal 1: Backend
npm run start:backend

# Terminal 2: Frontend  
npm run start:frontend

# Terminal 3: Electron App
npm run electron:dev
```

## 🎯 Usage Examples

### Enterprise Application Development
```
"Build a complete e-commerce platform with React frontend, Python FastAPI backend, PostgreSQL database, user authentication, payment processing, and Docker deployment"
```

### Quantitative Trading
```
"Develop and backtest a momentum trading strategy with risk management, optimize parameters for maximum Sharpe ratio, and generate performance reports"
```

### System Automation
```
"Take screenshots of my screen every minute, extract text using OCR, summarize the content, and save insights to a daily report"
```

### Complex Multi-Stage Projects
```
"Create a full-stack crypto trading dashboard with real-time data, implement multiple trading strategies, add backtesting capabilities, set up CI/CD pipeline, and deploy to AWS"
```

## 🏗️ System Architecture

### Frontend (React + TypeScript)
```
src/
├── components/
│   ├── LocalAIChat.tsx      # Chat interface
│   └── TaskDashboard.tsx    # Multi-agent progress monitoring
├── lib/
│   └── api.ts               # Backend API client
└── App.tsx                  # Main application
```

### Backend (FastAPI + Python)
```
backend/
├── main.py                  # FastAPI app with multi-agent orchestration
├── multi_agent.py           # Agent coordination system
├── enterprise_tools.py      # Development and deployment tools
├── context_agent.py         # Memory and system awareness
├── quant/
│   └── trading_system.py    # Quantitative trading engine
├── tools.py                 # OS automation tools
└── memory.py                # ChromaDB vector storage
```

### Electron Shell
```
electron-main.js             # Simplified Electron wrapper
preload.js                   # Security context bridge
```

## 🔧 API Endpoints

### Multi-Agent Coordination
- `POST /v1/chat/completions` - OpenAI-compatible chat with agent orchestration
- `POST /v1/tasks/submit` - Submit high-level objectives for autonomous execution
- `GET /v1/tasks/{session_id}/status` - Monitor task progress and agent coordination
- `GET /v1/tasks` - List all active and completed sessions

### Enterprise Development
- `POST /api/enterprise/write-file` - Create/modify files
- `POST /api/enterprise/run-shell` - Execute shell commands
- `POST /api/enterprise/git-init` - Initialize Git repositories
- `POST /api/enterprise/create-project` - Scaffold complete projects
- `POST /api/enterprise/docker-build` - Build Docker images
- `POST /api/enterprise/deploy-local` - Deploy applications locally

### Quantitative Trading
- `GET /api/quant/strategies` - List available trading strategies
- `POST /api/quant/backtest` - Run strategy backtests
- `POST /api/quant/optimize` - Optimize strategy parameters
- `GET /api/quant/results` - Get historical backtest results

### System Automation
- `POST /api/tools/click` - Mouse click operations
- `POST /api/tools/type` - Keyboard input
- `GET /api/tools/clipboard` - Read clipboard contents
- `POST /api/screenshot/screenshot` - Capture and analyze screenshots

## 🧪 Testing & Validation

### Run Integration Tests
```bash
# Start backend first
npm run start:backend

# Run comprehensive test suite
cd backend
source venv/bin/activate
python -m pytest tests/test_integration.py -v
```

### Manual Testing Flow
1. **Launch System**: `npm start`
2. **Access Dashboard**: Navigate to Task Dashboard
3. **Submit Complex Task**: Try building a trading bot
4. **Monitor Progress**: Watch agent coordination in real-time
5. **Verify Results**: Check generated code and deployment

## 🚀 Advanced Features

### Custom Agent Development
```python
# Add new specialized agents
class DataScientistAgent(TradingStrategy):
    def analyze_market_trends(self, data):
        # Custom market analysis logic
        pass
```

### Strategy Optimization
```python
# Optimize trading parameters
param_ranges = {
    'window': [10, 20, 30],
    'threshold': [0.01, 0.02, 0.03]
}
result = quant_system.optimize_strategy('momentum', 'BTCUSD', start_date, end_date, param_ranges)
```

### Enterprise Deployment
```bash
# Build production package
npm run package

# Deploy with Docker
docker build -t autonomous-ai-agent .
docker run -p 8001:8001 -p 3000:3000 autonomous-ai-agent
```

## 🔒 Security & Privacy

- **Fully Local**: No external API calls except to local Ollama
- **Data Isolation**: All processing occurs on local machine
- **Sandboxed Execution**: Docker containers for safe code execution
- **Audit Trail**: Complete logging of all agent actions and decisions

## 🛠️ Development

### Adding New Tools
1. Implement tool function in `backend/enterprise_tools.py`
2. Add API endpoint in `backend/main.py`
3. Update frontend API client in `src/lib/api.ts`
4. Test with integration test suite

### Custom Trading Strategies
1. Extend `TradingStrategy` class in `backend/quant/trading_system.py`
2. Register strategy in `main.py`
3. Add strategy-specific optimization parameters
4. Test with backtesting engine

### Agent Customization
1. Modify agent prompts in `backend/multi_agent.py`
2. Add new agent roles and capabilities
3. Update coordination logic
4. Test multi-agent workflows

## 📊 Performance Metrics

- **Task Completion Rate**: >90% for well-defined objectives
- **Code Quality**: Production-ready with testing and documentation
- **Speed**: Complex applications built in 15-30 minutes
- **Accuracy**: High-fidelity implementation of specifications

## 🚨 Troubleshooting

### Backend Issues
```bash
# Check Ollama connection
curl http://localhost:11434/api/tags

# Verify Python environment
cd backend && source venv/bin/activate && python -c "import fastapi; print('FastAPI OK')"

# Check backend logs
tail -f backend/logs/server.log
```

### Frontend Issues
```bash
# Check environment variables
cat .env.local

# Verify API connectivity
curl http://127.0.0.1:8001/health

# Clear build cache
npm run clean && npm run build
```

### Agent Coordination Issues
```bash
# Check agent status
curl http://127.0.0.1:8001/v1/tasks

# Monitor agent interactions
curl http://127.0.0.1:8001/v1/tasks/{session_id}/status

# Review context database
# ChromaDB data stored in backend/chroma_db/
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Implement changes with tests
4. Submit pull request with detailed description

## 📄 License

MIT License - Build the future of autonomous AI agents

---

**⚡ Ready to revolutionize your development workflow with autonomous AI agents? Start building enterprise-grade applications and trading systems with a single command!** 
