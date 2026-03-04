# Demo Template: Python Backend

Python backend section built using [FastAPI](https://fastapi.tiangolo.com/). The backend is managed using uv for dependency management, offering a RESTful API.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- Python backend with a RESTful API powered by FastAPI
- Dependency management with uv ([More info](https://docs.astral.sh/uv/))
- Easy setup and configuration

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.13 (but less than 3.14)
- uv (install via [uv's official documentation](https://docs.astral.sh/uv/getting-started/installation/))

For complete setup instructions, including how to create a new repository and clone it, please refer to the [parent README](../README.md).

## Getting Started

Follow these steps to set up the backend project locally. For detailed instructions on creating a new repository and using GitHub Desktop, please refer to the [parent README](../README.md).

### Backend Setup

1. (Optional) Set your project description and author information in the `pyproject.toml` file:
   ```toml
   description = "Your Description"
   authors = ["Your Name <you@example.com>"]
2. Open the project in your preferred IDE (the standard for the team is Visual Studio Code).
3. Open the Terminal within Visual Studio Code.
4. Ensure you are in the root project directory where the `makefile` is located.
5. Execute the following commands:
  - uv initialization
    ````bash
    make uv_init
    ````
  - uv sync
    ````bash
    make uv_sync
    ````
6. Verify that the `.venv` folder has been generated within the `/backend` directory.

## Running the Application

The backend service now includes integrated A2A (Agent-to-Agent) protocol support with automatic agent startup.

### Option 1: Quick Start (Recommended) 

Use the provided startup script that handles everything automatically:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Run the startup script:
   ```bash
   ./start.sh
   ```

This script will:
- Activate the virtual environment
- Sync dependencies  
- Start the FastAPI backend service on port 8000
- Automatically start all required services:
  - **Shopping Agent API** - integrated into main backend service (port 8000)
  - Merchant Agent (port 8001)
  - Credentials Provider Agent (port 8002)
  - Merchant Payment Processor Agent (port 8003)  
  - Auditor Agent (port 8004)
- Set up proper logging for all services

### Option 2: Manual Start

After setting up the backend dependencies, you can run the development server manually:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Start the FastAPI development server:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. The backend API will be accessible at http://localhost:8000

**Note**: With the manual start, the A2A agents are still started automatically via the FastAPI lifespan manager.

## 🎯 Architecture Overview

```
NextJS Frontend ←→ Backend API (8000) ←→ A2A Agents 
                         ↓               ├─ Merchant Agent (8001)
                   Shopping API          ├─ Credentials Provider (8002) 
                   (/api/v1/shopping)    ├─ Payment Processor (8003)
                                         └─ Auditor Agent (8004)
                                         └─ Mandate Ledger (5000)
```

### Available Endpoints

**Backend Service (Port 8000) - Unified API:**
- **Backend API**: http://localhost:8000
- **Shopping Chat**: http://localhost:8000/api/v1/shopping/chat
- **Start Session**: http://localhost:8000/api/v1/shopping/start-session
- **Session Status**: http://localhost:8000/api/v1/shopping/session/{session_id}
- **Health Check**: http://localhost:8000/health (includes agent status)
- **Agent Status**: http://localhost:8000/api/shopping/agents/status
- **API Docs**: http://localhost:8000/docs (Swagger UI)

**Individual A2A Agents:**
- **Merchant Agent**: http://localhost:8001/a2a/merchant_agent
- **Credentials Provider**: http://localhost:8002/a2a/credentials_provider
- **Payment Processor**: http://localhost:8003/a2a/merchant_payment_processor_agent

### Environment Variables

Make sure to set up the following environment variables (in `.env` file in project root):

- `GOOGLE_API_KEY`: Your Google API key for agent LLM functionality
- `GOOGLE_GENAI_USE_VERTEXAI`: Set to "true" to use Vertex AI with Application Default Credentials instead of API key

**Note**: If port 8000 is already in use (e.g., by Docker containers), either stop the containers with `make clean` or use a different port like `--port 8001`.
