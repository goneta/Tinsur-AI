# Google AI Agent Bake Off 2025 - Multi-Agent Banking System

This project was built as part of Google's AI Agent Bake Off 2025 challenge, where I reimagined retail banking through intelligent multi-agent systems powered by Google's Agent Development Kit (ADK), the Agent-to-Agent (A2A) Protocol, and the Gemini API.

## 🎯 What This Project Does

This multi-agent banking system transforms the traditional banking experience by providing proactive, intelligent financial guidance through specialized AI agents. Instead of static chatbots, users interact with a sophisticated orchestrator that routes queries to domain-specific agents, each equipped to handle different aspects of personal finance.

### The Agents

The system consists of six specialized agents working together:

- **Chat Orchestrator** - Intelligently routes user queries to the appropriate specialist agent
- **Spending Agent** - Analyzes transactions, budgets, and daily expenses
- **Perks Agent** - Manages banking perks, rewards, and account benefits
- **Portfolio Agent** - Provides investment portfolio analysis and market insights
- **Goals Agent** - Helps with financial goal setting and savings tracking
- **Advisors Agent** - Offers financial advisory services and professional guidance

Each agent connects to Cymbal Bank's backend services through the A2A protocol, enabling seamless communication and data exchange between agents.

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 15.4.6 with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **Port**: 3000 (default)

### Backend
- **Framework**: Google Agent Development Kit (ADK)
- **Protocol**: Agent-to-Agent (A2A) for inter-agent communication
- **Language**: Python (3.10+)
- **Package Manager**: uv
- **AI Model**: Gemini 2.5 Flash

### Agent Ports
- Chat Orchestrator: `8090`
- Spending Agent: `8081`
- Perks Agent: `8082`
- Portfolio Agent: `8083`
- Goals Agent: `8084`
- Advisors Agent: `8085`

## 🚀 Getting Started

### Prerequisites

Before running the project, make sure you have:

- **Node.js** (v20+)
- **Python** (3.10-3.12)
- **uv** (Python package manager) - [Install here](https://github.com/astral-sh/uv)
- **Google API Key** with Gemini API access

### Setup Instructions

#### 1. Configure Environment Variables

You need to add your `GOOGLE_API_KEY` to the `.env` file in each agent directory:

```bash
# Add your API key to each of these files:
agents/spending_snapshot_agent/spending_snapshot_agent/.env
agents/perks_snapshot_agent/perks_snapshot_agent/.env
agents/portfolio_snapshot_agent/portfolio_snapshot_agent/.env
agents/goals_snapshot_agent/goals_snapshot_agent/.env
agents/advisors_snapshot_agent/advisors_snapshot_agent/.env
agents/chat/chat/.env
```

Each `.env` file should contain:
```
GOOGLE_API_KEY=your_api_key_here
```

#### 2. Start the Agents

Open a terminal and navigate to the agents directory:

```bash
cd agents
make agents
```

This will start all agents simultaneously on their respective ports.

#### 3. Start the Frontend

Open a **second terminal** and start the Next.js development server:

```bash
cd frontend
npm install  # Only needed on first run
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 💡 How It Works

1. **User Interaction**: Users interact with the frontend interface, which provides a modern banking dashboard
2. **Query Routing**: The Chat Orchestrator receives user queries and intelligently routes them to the appropriate specialist agent
3. **Agent Processing**: Each specialist agent uses the Cymbal Bank Agent Wrapper to communicate with backend services via A2A protocol
4. **Data Retrieval**: Agents fetch relevant data (transactions, profile, goals, etc.) from Cymbal Bank's API
5. **Response Generation**: Agents analyze the data and generate intelligent, context-aware responses using Gemini
6. **User Response**: The orchestrator returns the response to the user through the frontend

## 🛠️ Technologies Used

- **[Google Agent Development Kit (ADK)](https://github.com/google/adk)** - Framework for building multi-agent systems
- **[Agent-to-Agent (A2A) Protocol](https://github.com/a2aproject/a2a)** - Standardized protocol for agent communication
- **[Gemini API](https://ai.google.dev/)** - Google's advanced AI model for natural language understanding
- **Next.js** - React framework for production-grade applications
- **Python** - Backend agent implementation
- **TypeScript** - Type-safe frontend development

## 📁 Project Structure

```
adk-bake-off/
├── agents/                          # Multi-agent backend
│   ├── chat/                        # Chat orchestrator agent
│   ├── spending_snapshot_agent/     # Spending analysis agent
│   ├── perks_snapshot_agent/        # Perks management agent
│   ├── portfolio_snapshot_agent/    # Portfolio analysis agent
│   ├── goals_snapshot_agent/        # Goals tracking agent
│   ├── advisors_snapshot_agent/     # Advisory services agent
│   └── Makefile                     # Agent startup commands
├── frontend/                        # Next.js frontend
│   ├── app/                         # Next.js app router
│   ├── components/                  # React components
│   └── lib/                         # Utility functions and types
└── refs/                           # Reference materials and samples
```

## 🎥 Built for Google's AI Agent Bake Off

This project was created as part of Google's AI Agent Bake Off 2025, a competition challenging developers to build the future of retail banking using cutting-edge AI agent technology. The challenge focused on:

- Creating seamless human-like interactions
- Offering proactive financial guidance
- Automating complex workflows with intelligence
- Demonstrating multi-agent orchestration
- Leveraging A2A protocol for agent communication

## 📝 Notes

- All agents must be running before the frontend can communicate with them
- The `make agents` command starts agents in the background - use `Ctrl+C` to stop all agents
- Each agent operates independently but communicates through the orchestrator
- The system uses the A2A protocol to enable standardized agent-to-agent communication

## 🔧 Troubleshooting

### Agents won't start
- Verify your `GOOGLE_API_KEY` is set in all `.env` files
- Check that ports 8081-8085 and 8090 are not in use
- Ensure Python 3.10+ is installed: `python --version`

### Frontend won't connect to agents
- Verify all agents are running (check terminal output)
- Ensure CORS is enabled (already configured in Makefile)
- Check browser console for connection errors

### Module not found errors
- Run `uv sync` in the agents directory to install dependencies
- Run `npm install` in the frontend directory

---

Built with ❤️ for Google's AI Agent Bake Off 2025

