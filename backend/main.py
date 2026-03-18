import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import json

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from pydantic import BaseModel, Field

from dotenv import load_dotenv

# Setup logging BEFORE any agent imports to capture import debug logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

from routers import mandate_ledger
from routers import shopping_router
from agents_manager import agents_manager
from agents.common.genai_client_manager import cleanup_genai_client

# Import the ADK shopping agent and Runner (following ADK FastAPI pattern)
from agents.roles.shopping_agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.genai import types

# FastAPI models for shopping agent integration
class ShoppingRequest(BaseModel):
    message: str
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context: Optional[Dict[str, Any]] = None

class ShoppingResponse(BaseModel):
    response: str
    session_id: str
    user_id: str 
    status: str = "success"
    data: Optional[Dict[str, Any]] = None
    agent_state: Optional[Dict[str, Any]] = None

# Setup ADK services (following ADK FastAPI pattern)
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
memory_service = InMemoryMemoryService()
#credential_service = InMemoryCredentialService()

# Create the ADK Runner for the shopping agent
shopping_runner = Runner(
    app_name="shopping_agent",
    agent=root_agent,
    artifact_service=artifact_service,
    session_service=session_service,
    memory_service=memory_service,
    #credential_service=credential_service,
)

async def call_shopping_agent(message: str, session_id: str, user_id: str) -> Dict[str, Any]:
    """Call the ADK shopping agent using the Runner pattern (same as ADK FastAPI)"""
    try:
        logger.info(f"Calling shopping agent with message: {message}")
        
        # Ensure session exists (minimal ADK requirement)
        session = await session_service.get_session(
            app_name="shopping_agent", 
            user_id=user_id, 
            session_id=session_id
        )
        
        if not session:
            session = await session_service.create_session(
                app_name="shopping_agent",
                user_id=user_id,
                session_id=session_id
            )
        
        # Call the agent with the actual user message using the module-level shopping_runner
        content_message = types.Content(role="user", parts=[types.Part.from_text(text=message)],)
        
        events = [
            event
            async for event in shopping_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content_message,
            )
        ]
        
        logger.info(f"Received {len(events)} events from agent")
        
        # Extract response text from events
        response_text = ""
        for event in events:
            # Extract text from ADK Event objects properly
            if hasattr(event, 'content') and event.content:
                # Handle Content object with parts
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text + "\n"
                elif hasattr(event.content, 'text') and event.content.text:
                    response_text += event.content.text + "\n"
            elif hasattr(event, 'text') and event.text:
                response_text += event.text + "\n"
                
        response_text = response_text.strip() or "Hello! I'm your shopping assistant. What are you looking for today?"
        
        logger.info(f"Final response text: {response_text[:200]}...")
        
        return {
            "response": response_text,
            "session_id": session_id,
            "user_id": user_id,
            "status": "success",
            "events_count": len(events),
            "debug_info": {
                "message_sent": message,
                "session_existed": session is not None,
                "events_received": len(events)
            }
        }
        
    except Exception as e:
        logger.error(f"Error calling shopping agent: {e}")
        return {
            "response": f"I encountered an error: {str(e)}",
            "session_id": session_id,
            "user_id": user_id,
            "status": "error",
            "error": str(e)
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifecycle, including A2A agent startup and cleanup.
    """
    # Startup
    logger.info("Starting backend service with A2A agents...")
    
    try:
        # Start all A2A agents in background
        logger.info("About to start all A2A agents via agents_manager...")
        agents_manager.start_all_agents()
        
        # Check status after startup attempt
        agents_status = agents_manager.get_status()
        logger.info(f"A2A agents status after startup: {agents_status}")
        
        is_healthy = agents_manager.is_healthy()
        logger.info(f"A2A agents health check: {is_healthy}")
        
        if not is_healthy:
            logger.info("WARNING: Some A2A agents may not have started properly")
            
        logger.info("A2A agents startup completed")
        
        yield
        
    finally:
        # Cleanup
        logger.info("Shutting down A2A agents...")
        agents_manager.cleanup()
        
        # Cleanup GenAI client to prevent async cleanup issues
        logger.info("Cleaning up GenAI client...")  
        try:
            await cleanup_genai_client()
        except Exception as e:
            logger.error(f"Error during GenAI client cleanup: {e}")
            
        logger.info("Backend service shutdown completed")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mandate_ledger.router)
# Shopping agent router (ADK-powered conversational interface)
app.include_router(shopping_router.router, prefix="/api/shopping", tags=["shopping"])

# FastAPI Shopping Agent Endpoints
@app.post("/api/v1/shopping/chat", response_model=ShoppingResponse, tags=["Shopping Agent"])
async def shopping_chat(request: ShoppingRequest) -> ShoppingResponse:
    """
    Chat with the ADK shopping agent - main conversation interface
    """
    try:
        # if not agents_manager.is_healthy():
        #     raise HTTPException(
        #         status_code=503, 
        #         detail="A2A agents are not ready. Please ensure all agents are running."
        #     )
        
        result = await call_shopping_agent(
            message=request.message,
            session_id=request.session_id, 
            user_id=request.user_id
        )
        
        return ShoppingResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in shopping chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/shopping/start-session", tags=["Shopping Agent"])
async def start_shopping_session(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a new shopping session
    """
    session_id = str(uuid.uuid4())
    user_id = user_id or str(uuid.uuid4())
    
    # Initialize with a greeting
    result = await call_shopping_agent(
        message="Hello, I'd like to start shopping",
        session_id=session_id,
        user_id=user_id
    )
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "status": "started",
        "initial_response": result.get("response", "Welcome! How can I help you shop today?")
    }

@app.get("/api/v1/shopping/session/{session_id}", tags=["Shopping Agent"])
async def get_shopping_session(session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get shopping session state and conversation history
    """
    try:
        logger.info(f"Getting session app_name=shopping_agent")
        
        # Get session from ADK session service
        session = await session_service.get_session(
            app_name="shopping_agent", 
            user_id=user_id, 
            session_id=session_id
        )
        
        logger.info(f"Session retrieved: {session is not None}")
        
        if not session:
            logger.warning(f"Session not found")
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Safely extract session data
        session_data = {}
        try:
            # Try to get common session attributes safely
            if hasattr(session, '__dict__'):
                for key, value in session.__dict__.items():
                    if key == 'events' and hasattr(value, '__iter__'):
                        # Special handling for events - convert to JSON-friendly format
                        events_json = []
                        try:
                            for event in value:
                                event_dict = {}
                                if hasattr(event, '__dict__'):
                                    for event_key, event_value in event.__dict__.items():
                                        try:
                                            # Test if this value can be JSON serialized
                                            json.dumps(event_value)
                                            event_dict[event_key] = event_value
                                        except (TypeError, UnicodeDecodeError, ValueError):
                                            # Convert problematic values to string
                                            event_dict[event_key] = str(event_value)
                                else:
                                    event_dict = str(event)
                                events_json.append(event_dict)
                            session_data[key] = events_json
                        except Exception:
                            # Fallback to string if events parsing fails
                            session_data[key] = str(value)
                    else:
                        try:
                            # Test if this value can be JSON serialized
                            json.dumps(value)
                            session_data[key] = value
                        except (TypeError, UnicodeDecodeError, ValueError):
                            # If it can't be serialized, convert to string representation
                            session_data[key] = str(value)
            elif hasattr(session, 'model_dump'):
                # Try model_dump but handle serialization errors
                try:
                    session_data = session.model_dump()
                except Exception:
                    session_data = {"raw": str(session)}
            else:
                session_data = {"raw": str(session)}
        except Exception as e:
            session_data = {"error": f"Could not extract session data: {str(e)}"}
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "session_exists": True,
            "session_data": session_data
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error getting session for user {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Session service error: {str(e)}")

router = APIRouter()

@app.get("/")
async def read_root(request: Request):
    return {
        "message": "Backend server with ADK Shopping Agent FastAPI integration",
        "service": "Backend API with Shopping Agent (ADK-powered)", 
        "version": "1.0.0",
        "agents": agents_manager.get_status(),
        "description": "ADK shopping agent wrapped in FastAPI endpoints for NextJS integration",
        "endpoints": {
            "shopping_chat": "/api/v1/shopping/chat",
            "start_session": "/api/v1/shopping/start-session",
            "session_info": "/api/v1/shopping/session/{session_id}",
            "shopping_health": "/api/shopping/health",
            "agent_status": "/api/shopping/agents/status", 
            "health": "/health",
            "api_docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    agents_status = agents_manager.get_status()
    is_healthy = agents_manager.is_healthy()
    
    # Log agent status for debugging
    logger.info(f"Health check - agents status: {agents_status}")
    logger.info(f"Health check - is_healthy: {is_healthy}")
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "backend",
        "message": "Backend service is running",
        "agents": agents_status,
        "agents_healthy": is_healthy,
        "agent_count": len(agents_status) if isinstance(agents_status, dict) else 0
    }