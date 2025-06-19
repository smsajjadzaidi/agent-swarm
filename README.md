# agent-swarm


# Agent Swarm 🤖

A sophisticated multi-agent chatbot system designed for InfinitePay, featuring intelligent routing, knowledge retrieval, and customer support capabilities.

## 🚀 Features

- **Intelligent Agent Routing**: Automatically routes user queries to the most appropriate specialized agent
- **Knowledge Agent**: Provides detailed information about InfinitePay products and services using RAG (Retrieval-Augmented Generation)
- **Support Agent**: Handles customer support issues, account management, and ticket creation
- **Personality Layer**: Applies friendly, empathetic personality to all responses
- **Web Search Integration**: Augments knowledge with real-time web search capabilities
- **FastAPI REST API**: Production-ready API endpoints for integration
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

The system consists of three main agents working together:

### 1. Router Agent (`agents/router_agent.py`)
- **Purpose**: Entry point that analyzes incoming messages and routes them to appropriate specialized agents
- **Features**:
  - Fast keyword-based routing for common queries
  - LLM-based classification for ambiguous cases
  - Personality layer application for consistent tone
  - Support for both knowledge and support queries

### 2. Knowledge Agent (`agents/knowledge_agent.py`)
- **Purpose**: Handles product information, pricing, and general knowledge queries
- **Features**:
  - RAG-based retrieval from InfinitePay documentation
  - Web search integration via Serper API
  - Automatic source citation
  - Tool-based architecture for flexible query handling

### 3. Support Agent (`agents/support_agent.py`)
- **Purpose**: Manages customer support issues and account-related queries
- **Features**:
  - Account status checking
  - Support ticket creation and tracking
  - User authentication simulation
  - Empathetic response generation

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- Serper API key (for web search functionality)
- Redis (optional, for caching)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent-swarm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   OPENAI_MODEL=gpt-4o
   ```

## 🚀 Quick Start

### Running the API Server

```bash
# Start the FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST `/chat`
Send a message to the chatbot:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are the fees for credit card processing?",
       "user_id": "user123"
     }'
```

**Response Format:**
```json
{
  "response": "Friendly, empathetic response...",
  "source_agent_response": "Raw agent response...",
  "agent_workflow": [
    {
      "agent_name": "KnowledgeAgent",
      "tool_calls": {
        "company_docs": "Retrieved information...",
        "search_web": "Web search results..."
      }
    }
  ]
}
```

### Running Tests

```bash
pytest test_agent_swarm.py -v
```

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t agent-swarm .

# Run the container
docker run -p 8000:8000 --env-file .env agent-swarm
```


## 📚 Knowledge Base

The system automatically builds a knowledge base from InfinitePay's website content:

- **Automatic Crawling**: Scrapes predefined InfinitePay URLs
- **Vector Storage**: Uses FAISS for efficient similarity search
- **Chunking**: Intelligent text splitting for optimal retrieval
- **Persistence**: Saves index to disk for faster subsequent loads

### Rebuilding Knowledge Base

```bash
python knowledge_base_builder.py
```

## 🔧 Configuration

Key configuration options in `config.py`:

- **OpenAI Settings**: Model selection and API configuration
- **Knowledge Base**: Directory paths and retrieval parameters
- **Agent Personalities**: Customizable agent behaviors
- **InfinitePay URLs**: List of websites to crawl for knowledge

## 🧪 Testing

The project includes comprehensive tests:

- **Unit Tests**: Individual agent functionality
- **Integration Tests**: End-to-end API testing
- **Parameterized Tests**: Multiple scenarios and edge cases

Run tests with:
```bash
pytest test_agent_swarm.py -v
```

## 📁 Project Structure

```
agent-swarm/
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── router_agent.py       # Main routing logic
│   ├── knowledge_agent.py    # Product knowledge handling
│   └── support_agent.py      # Customer support
├── knowledge_base/           # Vector database storage
├── app.py                   # FastAPI application
├── config.py               # Configuration settings
├── knowledge_base_builder.py # Knowledge base construction
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── test_agent_swarm.py     # Test suite
└── README.md               # This file
```


