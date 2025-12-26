# Debate Agent - Project Structure

## Overview
All Python files and related resources have been organized into the `serve` folder with a clean, modular structure.

## Directory Structure

```
debateAgent/
├── .env                          # Environment variables (API keys, etc.)
├── .gitignore
├── LICENSE
├── README.md                     # Main project README
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── uv.lock                      # Lock file for dependencies
│
└── serve/                       # Main application folder
    ├── API_README.md            # REST API documentation
    ├── ConfigService.py         # Configuration management service
    ├── llm_service.py           # LLM service wrapper
    ├── agent_service.py         # Core debate agent workflow service
    │
    ├── affirmative_agent.py     # Affirmative team agent
    ├── negative_agent.py        # Negative team agent
    ├── referee_agent.py         # Referee/judge agent
    │
    ├── debate_api.py            # REST API endpoints (NEW)
    ├── debate_ui.py             # Gradio web UI
    ├── main.py                  # CLI entry point
    ├── test_api_client.py       # API test client (NEW)
    │
    └── prompts/                 # Prompt templates folder
        ├── affirmative_prompt_template.txt
        ├── negative_prompt_template.txt
        ├── judge_prompt_template.txt
        ├── summarize_prompt_template.txt
        └── topic_prompt_template.txt

├── client/                      # React Frontend (NEW)
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── README.md
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── components/
        │   ├── DebateApp.jsx    # Main debate interface
        │   └── DebateApp.css    # Styles
        └── services/
            └── api.js           # API integration service

## Key Components

### Core Services

1. **agent_service.py** - `DebateAgentService`
   - Core workflow orchestration using LangGraph
   - Handles decision making, web search, summarization
   - Manages the debate agent state machine

2. **llm_service.py** - `LLMService`
   - Wrapper for LLM API calls
   - Handles OpenAI/DeepSeek integration
   - Manages retries and error handling

3. **ConfigService.py** - `ConfigService`
   - Configuration management
   - Temperature and model settings

### Agent Classes

4. **affirmative_agent.py** - `AffirmativeAgent`
   - Generate affirmative team positions
   - Create arguments and rebuttals
   - Generate closing statements

5. **negative_agent.py** - `NegativeAgent`
   - Generate negative team positions
   - Create counter-arguments and rebuttals
   - Generate closing statements

6. **referee_agent.py** - `RefereeAgent`
   - Judge debates
   - Evaluate arguments
   - Provide scoring and reasoning

### User Interfaces

7. **client/** - React Frontend (NEW)
   - Modern, responsive web interface
   - Built with React, Vite, and Axios
   - Real-time interaction with debate API

8. **debate_api.py** - REST API (NEW)
   - FastAPI-based REST endpoints
   - Complete API for all debate functions
   - Auto-generated documentation at `/docs`

9. **debate_ui.py** - Gradio UI (Legacy)
   - Interactive web interface
   - Multi-round debate support
   - Real-time AI generation

10. **main.py** - CLI Entry Point
    - Command-line interface
    - Launches Gradio UI

### Testing & Documentation

11. **test_api_client.py** - API Test Client (NEW)
    - Demonstrates API usage
    - Runs complete debates programmatically
    - Example integration code

12. **API_README.md** - API Documentation (NEW)
    - Complete endpoint reference
    - Request/response examples
    - Usage examples in multiple languages

## Running the Application

### Option 1: React Client (Recommended)

1. Start the API server:
   ```bash
   cd serve
   python debate_api.py
   ```

2. Start the React client (in a new terminal):
   ```bash
   cd client
   npm install
   npm run dev
   ```

   Access at: `http://localhost:5173`

### Option 2: Gradio Web UI

```bash
cd serve
python main.py
```

Access at: `http://localhost:7860`

### Option 3: REST API

```bash
cd serve
python debate_api.py
```

Access at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Option 4: Test Client

```bash
cd serve
# First, start the API in another terminal
python debate_api.py

# Then run the test client
python test_api_client.py
```

## API Endpoints Summary

### Topic Generation
- `POST /api/topics/generate` - Generate both team options
- `POST /api/topics/affirmative` - Generate affirmative option
- `POST /api/topics/negative` - Generate negative option

### Affirmative Team
- `POST /api/affirmative/statement` - Generate statement
- `POST /api/affirmative/rebuttal` - Generate rebuttal
- `POST /api/affirmative/closing` - Generate closing argument

### Negative Team
- `POST /api/negative/statement` - Generate statement
- `POST /api/negative/rebuttal` - Generate rebuttal
- `POST /api/negative/closing` - Generate closing argument

### Judging
- `POST /api/judge/debate` - Judge complete debate

### Configuration
- `GET /api/config/temperature` - Get temperature setting
- `POST /api/config/temperature` - Set temperature setting

## Dependencies

### Core Dependencies
- `gradio>=4.0.0` - Web UI framework
- `httpx>=0.24.0` - HTTP client
- `tenacity>=8.0.0` - Retry logic
- `openai>=1.0.0` - OpenAI API client
- `python-dotenv>=1.0.0` - Environment variables

### REST API Dependencies (NEW)
- `fastapi>=0.104.0` - Modern web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic>=2.0.0` - Data validation

### Frontend Dependencies (NEW)
- `react` - UI library
- `vite` - Build tool
- `axios` - HTTP client
- `react-icons` - Icon library

## Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional LLM Configuration
MODEL_NAME=gpt-4
TEMPERATURE=0.7
```

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd client
npm install
```

## Changes Made

### File Organization
1. ✅ Moved all Python files to `serve/` folder
2. ✅ Moved all template files to `serve/prompts/` folder
3. ✅ Updated template path resolution in `agent_service.py`

### New Features
4. ✅ Created `debate_api.py` - Complete REST API
5. ✅ Created `client/` - Modern React Frontend
6. ✅ Created `test_api_client.py` - API test client
7. ✅ Created `API_README.md` - API documentation
8. ✅ Updated `requirements.txt` - Added FastAPI dependencies

### Code Improvements
9. ✅ Fixed prompt template loading to use `prompts/` subdirectory
10. ✅ Added proper error handling in API endpoints
11. ✅ Included CORS support for cross-origin requests
12. ✅ Auto-generated API documentation (Swagger/ReDoc)

## Next Steps

### Recommended Improvements
- [ ] Add authentication to API endpoints
- [ ] Implement rate limiting
- [ ] Add database for storing debate history
- [ ] Add WebSocket support for real-time updates
- [ ] Implement caching for common requests
- [ ] Add comprehensive test suite
- [ ] Set up CI/CD pipeline

### Production Deployment
- [ ] Build React frontend for production (`npm run build`)
- [ ] Configure production ASGI server (e.g., gunicorn)
- [ ] Set up reverse proxy (nginx/Apache) to serve frontend and API
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and logging
- [ ] Implement backup and recovery
- [ ] Configure auto-scaling

## Support

For API documentation, visit: `http://localhost:8000/docs` when the API is running.

For issues or questions, refer to the main README.md or API_README.md.
