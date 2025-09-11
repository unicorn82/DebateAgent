# DebateAgent

A sophisticated AI-powered debate application that enables structured debates between human and/or  AI agents, supporting multiple rounds of arguments, rebuttals, and automated judging.

## 🎯 Overview

DebateAgent is an interactive debate platform that facilitates formal debates using AI agents. The application supports both agent-vs-agent and agent-vs-human debates with structured rounds, automated argument generation, and AI-powered judging.

## ✨ Features

### 🤖 AI-Powered Debate Agents
- **Affirmative Agent**: Generates strong pro-arguments supporting the debate topic
- **Negative Agent**: Creates compelling counter-arguments opposing the topic
- **Referee Agent**: Manages debate flow, generates topics, and provides impartial judging

### 🎪 Interactive Web Interface
- **Gradio-based UI**: Clean, intuitive web interface for debate management
- **Multi-round Support**: Configurable number of debate rounds (default: 3)
- **Real-time Generation**: AI-powered argument generation with live updates
- **Structured Layout**: Organized display of arguments, rebuttals, and final summaries

### 🏆 Advanced Judging System
- **Comprehensive Scoring**: Evaluates arguments, rebuttals, evidence, and organization
- **Detailed Feedback**: Provides improvement suggestions for both teams
- **JSON-structured Results**: Standardized judging output with scores and reasoning
- **Multiple Display Options**: Winner announcement, detailed scores, and reasoning

### 🔧 Flexible Configuration
- **Multiple LLM Providers**: Support for OpenAI and DeepSeek APIs
- **Configurable Parameters**: Adjustable temperature, model selection, and timeouts
- **Environment-based Setup**: Secure API key management via environment variables

## 🏗️ Architecture


### Agent Responsibilities

- **🟢 Affirmative Agent**: Constructs logical arguments supporting the topic, addresses counterarguments, provides evidence-based reasoning
- **🔴 Negative Agent**: Identifies flaws in affirmative positions, presents alternative viewpoints, challenges assumptions
- **⚖️ Referee Agent**: Generates debate topics, manages debate flow, provides impartial scoring and feedback

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- API keys for supported LLM providers (OpenAI/DeepSeek)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd debateAgent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with your API configurations:
   ```env
   # Referee Agent Configuration
   REFEREE_PROVIDER=openai
   REFEREE_API_KEY=your_openai_api_key
   REFEREE_MODEL=gpt-4
   
   # Affirmative Agent Configuration
   AFFIRMATIVE_PROVIDER=openai
   AFFIRMATIVE_API_KEY=your_openai_api_key
   AFFIRMATIVE_MODEL=gpt-3.5-turbo
   
   # Negative Agent Configuration
   NEGATIVE_PROVIDER=deepseek
   NEGATIVE_API_KEY=your_deepseek_api_key
   NEGATIVE_MODEL=deepseek-chat
   ```

### Running the Application

**Launch the main interface**:
```bash
python debate_ui.py
```


The application will start a local web server (typically at `http://localhost:7860`).

## 🎮 Usage Guide

### Starting a Debate

1. **Enter Topic**: Input your debate topic in the main text field
2. **Generate Options**: Click "Generate Team Options (AI)" or input your own affirmative and negative team options to create structured  options.
3. **Configure Rounds**: Set the number of debate rounds (1-3)
4. **Generate Arguments**: Input your arguments or use AI buttons to generate arguments for each round
5. **Final Summaries**: Input your own summaries or use AI button to generate closing arguments for both teams
6. **Judge Winner**: Click "Judge Winner (AI)" for automated scoring and winner determination

### Manual vs AI Mode

- **🤖 AI Mode**: Click AI buttons next to each text field for automated content generation
- **✍️ Manual Mode**: Type arguments directly into text fields
- **🔀 Hybrid Mode**: Mix AI-generated and manual content as needed

## 🔧 Configuration

### Supported LLM Providers

- **OpenAI**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **DeepSeek**: deepseek-chat

### Environment Variables

Each agent can be configured independently:

```env
{AGENT}_PROVIDER=openai|deepseek
{AGENT}_API_KEY=your_api_key
{AGENT}_MODEL=model_name
```

Where `{AGENT}` can be: `REFEREE`, `AFFIRMATIVE`, `NEGATIVE`

## 📊 Judging Criteria

The AI judge evaluates debates based on:

- **🎯 Clarity & Structure**: Logical organization and clear presentation
- **📚 Evidence & Reasoning**: Use of facts, data, and logical arguments
- **🔄 Rebuttal Quality**: Engagement with opposing arguments
- **🤝 Team Cohesion**: Consistency across team members
- **🏁 Summary Strength**: Effectiveness of closing arguments

## 🛠️ Dependencies

```txt
gradio>=4.0.0          # Web interface framework
httpx>=0.24.0          # HTTP client for API calls
tenacity>=8.0.0        # Retry logic for API calls
openai>=1.0.0          # OpenAI API client
python-dotenv>=1.0.0   # Environment variable management
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🔮 Future Enhancements

- **Modify AI prompt at runtime**: Allow users to customize the AI prompts used for generating arguments and summaries.
- **Custom judging criteria**: Allow users to define their own judging criteria for evaluating debates.
- **Add voice support**: Add voice input and output capabilities for a more interactive user experience.
- **Multi-language support**: Expand the application to support debates in multiple languages.
- **Tournament-style competitions**: Introduce features for organizing and competing in structured debate tournaments.

---

**Ready to debate?** 🎭 Launch the application and let the AI agents engage in structured, intelligent discourse on any topic of your choice!