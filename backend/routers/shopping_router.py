"""
Shopping Router for A2A Agent integration.

This router provides REST API endpoints to interact with the A2A agents,
particularly the shopping agent and related agent communication flows.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from agents_manager import agents_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class ShoppingRequest(BaseModel):
    """Request model for shopping interactions."""
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"


class AgentResponse(BaseModel):
    """Response model from agent interactions."""
    response: str
    agent_name: str
    success: bool
    session_id: str


@router.get("/health")
async def get_shopping_health():
    """Check the health of shopping-related agents."""
    status = agents_manager.get_status()
    
    return {
        "status": "healthy" if agents_manager.is_healthy() else "degraded",
        "agents": status,
        "service": "shopping"
    }


@router.get("/agents/status")
async def get_agents_status():
    """Get detailed status of all A2A agents."""
    return agents_manager.get_status()


@router.post("/chat")
async def shopping_chat(request: ShoppingRequest) -> Dict[str, Any]:
    """
    Handle shopping chat requests through the A2A protocol.
    
    This endpoint provides a RESTful interface to the shopping agent,
    which communicates with other agents via the A2A protocol.
    """
    try:
        # For now, this is a placeholder that confirms agents are running
        # In a full implementation, this would:
        # 1. Send the request to the shopping agent 
        # 2. Handle the A2A communication flow
        # 3. Return the structured response
        
        if not agents_manager.is_healthy():
            raise HTTPException(
                status_code=503, 
                detail="Shopping agents are not ready"
            )
        
        # Placeholder response - in production this would communicate with agents
        response = {
            "response": f"Shopping agent received: {request.message}",
            "agent_name": "shopping_agent", 
            "success": True,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "agents_status": "running",
            "available_agents": ["merchant_agent", "credentials_provider_agent", "merchant_payment_processor_agent", "auditor_agent"]
        }
        
        # Helper function to sanitize user input before logging to prevent log injection
        def _sanitize_for_log(value: str, max_length: int = 200) -> str:
            import re
            sanitized = value.replace('\n', '\\n').replace('\r', '\\r')
            sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', sanitized)
            return sanitized[:max_length] + ('...[truncated]' if len(sanitized) > max_length else '')
        logger.info(
            f"Processed shopping request for user {_sanitize_for_log(str(request.user_id))}: {_sanitize_for_log(str(request.message)[:50])}..."
        )        
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing shopping request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart-agents")
async def restart_agents():
    """Restart all A2A agents - useful for development/debugging."""
    try:
        logger.info("Restarting A2A agents...")
        agents_manager.cleanup()
        agents_manager.start_all_agents()
        
        return {
            "status": "success",
            "message": "Agents restarted",
            "agents": agents_manager.get_status()
        }
    except Exception as e:
        logger.error(f"Error restarting agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart agents: {e}")


@router.get("/")
async def shopping_root():
    """Shopping service root endpoint."""
    return {
        "service": "shopping",
        "version": "1.0.0", 
        "description": "A2A Agent Shopping Service",
        "agents_healthy": agents_manager.is_healthy()
    }