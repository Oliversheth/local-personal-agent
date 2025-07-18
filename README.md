# Local AI Assistant

A fully local, offline macOS desktop AI assistant powered by Ollama models with OS-level automation capabilities.

## Features

- **Local AI Processing**: Uses Ollama models (`codellama:instruct` & `deepseek-coder`) for all AI operations
- **Screenshot Analysis**: Capture and analyze screenshots with OCR
- **OS Automation**: Click, type, clipboard operations, and more
- **Vector Memory**: ChromaDB-powered context retrieval for enhanced conversations
- **Offline Operation**: No cloud dependencies - everything runs locally

## Prerequisites

1. **Node.js** (v16 or higher)
2. **Python 3.11+** with pip
3. **Ollama** installed and running with required models
4. **Tesseract OCR** for image text extraction

### Install Ollama Models

```bash
# Install required models
ollama pull codellama:instruct
ollama pull deepseek-coder

# Verify Ollama is running
ollama list
```

### Install Tesseract (macOS)

```bash
brew install tesseract
```

## Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd local-ai-assistant
npm install
```

2. **Setup Python backend**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
# Backend configuration is in backend/.env
# Frontend configuration is in .env.local
# Default settings should work for most setups
```

## Running the Application

### Development Mode

**Option 1: All services together**
```bash
npm run start
```

**Option 2: Services separately**
```bash
# Terminal 1: Backend
npm run start:backend

# Terminal 2: Frontend
npm run start:frontend

# Terminal 3: Electron (wait for frontend to be ready)
npm run electron:dev
```

### Production Build

```bash
npm run package
```

Built app will be in the `release/` folder.

## Usage

1. **Launch the app** - The AI assistant will open in a desktop window
2. **Take screenshots** - Click the camera button to capture and analyze screen content
3. **Use automation** - Ask the AI to perform actions like clicking, typing, or clipboard operations
4. **Natural conversation** - Chat with the AI about any topic, with context memory

### Example Commands

- "Take a screenshot and tell me what's on my screen"
- "Click on the button at coordinates (100, 200)"
- "Type 'Hello World' for me"
- "What's in my clipboard?"
- "Help me automate this task"

## System Architecture

- **Frontend**: React + TypeScript + Vite + Electron
- **Backend**: FastAPI + Python
- **AI Models**: Ollama (codellama:instruct, deepseek-coder)
- **Memory**: ChromaDB vector database
- **Automation**: PyAutoGUI, Tesseract OCR

## Configuration

### Backend Environment (backend/.env)
```
OLLAMA_URL=http://localhost:11434
CONTROL_MODEL=codellama:instruct
CODE_MODEL=deepseek-coder
```

### Frontend Environment (.env.local)
```
VITE_BACKEND_URL=http://127.0.0.1:8001/v1
VITE_APP_NAME=Local AI Assistant
```

## API Endpoints

### Chat API
- `POST /v1/chat/completions` - OpenAI-compatible chat completions
- `GET /v1/models` - List available models

### Screenshot API
- `POST /api/screenshot/screenshot` - Take and analyze screenshots
- `GET /api/screenshot/queue` - Get screenshot queue
- `DELETE /api/screenshot/queue/{id}` - Delete screenshot

### Automation Tools
- `POST /api/tools/click` - Click at coordinates
- `POST /api/tools/type` - Type text
- `GET /api/tools/clipboard` - Read clipboard
- `POST /api/tools/clipboard` - Write to clipboard

## Development Notes

### Adding New Tools
1. Add the tool function to `backend/tools.py`
2. Create API endpoint in `backend/tools_router.py`
3. Add client method to `src/lib/api.ts`

### Model Switching
The system automatically detects when coding tasks are requested and switches to the `deepseek-coder` model for better code generation.

### Memory System
Conversations and screenshot analyses are stored in ChromaDB for context retrieval in future interactions.

## Troubleshooting

### Backend Won't Start
- Check if Ollama is running: `ollama list`
- Verify Python environment: `which python` (should be in venv)
- Check port 8001 is free: `lsof -i :8001`

### Frontend Connection Issues
- Verify backend is running on port 8001
- Check CORS settings in backend
- Ensure environment variables are set correctly

### Screenshot/Automation Not Working
- Check if running in headless environment
- Verify display permissions on macOS
- Install required system dependencies

### OCR Issues
- Ensure Tesseract is installed: `tesseract --version`
- Check if image files are accessible
- Verify PIL/Pillow can read images

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details 
