"""
Auditor Router for A2A Agent integration.

This router provides REST API endpoints to interact with the auditor agent,
which handles payment verification, mandate history, and ledger integrity testing.
"""

import logging
import httpx
import json
import uuid
from typing import Dict, Any, Optional

# Try to import A2A framework components (they might not be available)
try:
    from agents.common.a2a_message_builder import A2aMessageBuilder
    from agents.common.payment_remote_a2a_client import PaymentRemoteA2aClient
    A2A_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    print(f"A2A Framework not available: {e}")
    A2A_FRAMEWORK_AVAILABLE = False
    A2aMessageBuilder = None
    PaymentRemoteA2aClient = None

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from agents_manager import agents_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# A2A Communication Configuration
AUDITOR_AGENT_URL = "http://localhost:8004/a2a/auditor_agent"
AUDITOR_AGENT_TIMEOUT = 30.0

# A2A Framework Client (if available)
auditor_agent_client = None
if A2A_FRAMEWORK_AVAILABLE and PaymentRemoteA2aClient:
    try:
        auditor_agent_client = PaymentRemoteA2aClient(
            name="auditor_agent",
            base_url=AUDITOR_AGENT_URL
        )
        print("✅ A2A Framework client initialized successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize A2A client: {e}")
        auditor_agent_client = None


async def call_auditor_agent_a2a(message: str, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Send A2A request to the auditor agent.
    
    Args:
        message: Natural language message for the auditor agent
        user_id: User identifier for the request
        
    Returns:
        Parsed response from the auditor agent
    """
    try:
        # Try different A2A communication approaches
        
        # Try multiple JSON-RPC methods in order of likelihood
        methods_to_try = ["chat", "process_message", "handle_message", "execute", "run", "invoke", "call"]
        
        logger.info(f"Sending A2A request to auditor agent: {message[:100]}...")
        
        for method_name in methods_to_try:
            logger.info(f"Trying JSON-RPC method: '{method_name}'")
            
            request_payload = {
                "jsonrpc": "2.0",
                "method": method_name,
                "params": {
                    "message": message,
                    "user_id": user_id,
                    "session_id": f"audit_session_{uuid.uuid4().hex[:8]}"
                },
                "id": str(uuid.uuid4())
            }
            
            logger.debug(f"A2A payload (method '{method_name}'): {json.dumps(request_payload, indent=2)}")
            
            async with httpx.AsyncClient(timeout=AUDITOR_AGENT_TIMEOUT) as client:
                response = await client.post(
                    AUDITOR_AGENT_URL,
                    json=request_payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Backend-Auditor-Router/1.0"
                    }
                )
                
                logger.info(f"A2A Response status: {response.status_code} for method '{method_name}'")
                
                if response.status_code == 200:
                    try:
                        rpc_response = response.json()
                        logger.debug(f"A2A Response for '{method_name}': {json.dumps(rpc_response, indent=2)}")
                        
                        if "error" in rpc_response:
                            error_code = rpc_response["error"].get("code") 
                            if error_code == -32601:  # Method not found
                                logger.info(f"Method '{method_name}' not found (-32601), trying next method...")
                                continue
                            elif error_code == -32600:  # Invalid request
                                logger.info(f"Method '{method_name}' validation error (-32600), trying next method...")
                                continue
                            else:
                                logger.error(f"A2A RPC error for '{method_name}': {rpc_response['error']}")
                                continue  # Try next method anyway
                        
                        elif "result" in rpc_response:
                            # SUCCESS! Found working method
                            logger.info(f"✅ SUCCESS! Method '{method_name}' worked!")
                            result = rpc_response.get("result", {})
                            
                            if isinstance(result, dict):
                                agent_response = result.get("text", result.get("response", result.get("message", "Agent completed successfully")))
                                tool_results = result.get("tool_results", result.get("data", result.get("results", [])))
                            else:
                                agent_response = str(result) if result else "Agent completed successfully"
                                tool_results = []
                            
                            return {
                                "success": True,
                                "agent_response": agent_response,
                                "tool_results": tool_results,
                                "agent_status": "completed",
                                "rpc_id": rpc_response.get("id"),
                                "raw_result": result,
                                "working_method": method_name
                            }
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response for method '{method_name}': {e}")
                        continue  # Try next method
                        
        logger.warning("All JSON-RPC methods failed, trying fallback approaches...")
        
        # Fallback: Try simple message POST without JSON-RPC wrapper
        logger.info("Trying direct message POST...")
        simple_payload = {
            "message": message,
            "user_id": user_id,
            "session_id": f"audit_session_{uuid.uuid4().hex[:8]}"
        }
        
        logger.debug(f"Simple payload: {json.dumps(simple_payload, indent=2)}")
        
        async with httpx.AsyncClient(timeout=AUDITOR_AGENT_TIMEOUT) as client:
            response = await client.post(
                AUDITOR_AGENT_URL,
                json=simple_payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Backend-Auditor-Router/1.0"
                }
            )
            
            logger.info(f"Simple POST Response status: {response.status_code}")
            response_text = response.text
            logger.info(f"Simple POST Response text (first 500 chars): {response_text[:500]}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"Simple POST Response JSON: {json.dumps(result, indent=2)}")
                    
                    # Handle different response formats
                    if isinstance(result, dict):
                        agent_response = result.get("response", result.get("text", result.get("message", "No response text")))
                        tool_results = result.get("tool_results", result.get("data", result.get("results", [])))
                        
                        # Check if the response is actually empty/placeholder
                        if not agent_response or agent_response == "No response text":
                            logger.warning("Auditor agent returned empty response - agent may not be processing the message correctly")
                            
                            # Try to extract any meaningful content from the response
                            if result:
                                # Look for any non-empty values in the response
                                content_keys = ["content", "output", "result", "answer", "audit_result"]
                                for key in content_keys:
                                    if result.get(key):
                                        agent_response = result[key]
                                        break
                                else:
                                    # If still no content, return raw result as string
                                    agent_response = f"Auditor agent response: {json.dumps(result)}"
                        
                        return {
                            "success": True,
                            "agent_response": agent_response,
                            "tool_results": tool_results,
                            "agent_status": "completed",
                            "raw_result": result,
                            "debug_info": {
                                "response_keys": list(result.keys()) if isinstance(result, dict) else None,
                                "raw_response_text": response_text[:200]  # First 200 chars for debugging
                            }
                        }
                    else:
                        return {
                            "success": True,
                            "agent_response": str(result) if result else "Empty response from auditor agent",
                            "tool_results": [],
                            "agent_status": "completed",
                            "raw_result": result,
                            "debug_info": {
                                "response_type": type(result).__name__,
                                "raw_response_text": response_text[:200]
                            }
                        }
                        
                except json.JSONDecodeError:
                    # Return as text
                    return {
                        "success": True,
                        "agent_response": response.text,
                        "tool_results": [],
                        "agent_status": "completed"
                    }
        
        # If we get here, something went wrong
        logger.error(f"All A2A approaches failed. Last status: {response.status_code}")
        return {
            "success": False,
            "error": f"Auditor agent returned status {response.status_code}",
            "agent_response": f"Unexpected response from auditor agent (HTTP {response.status_code})"
        }
            
    except httpx.TimeoutException:
        logger.error("Timeout communicating with auditor agent")
        return {
            "success": False,
            "error": "Auditor agent request timed out",
            "agent_response": "The auditor agent request timed out. Please try again."
        }
    except httpx.HTTPStatusError as e:
        error_text = ""
        try:
            error_body = e.response.json()
            error_text = f" - {error_body}"
        except:
            error_text = f" - {e.response.text}"
            
        logger.error(f"HTTP error communicating with auditor agent: {e.response.status_code}{error_text}")
        return {
            "success": False,
            "error": f"Auditor agent HTTP error: {e.response.status_code}",
            "agent_response": f"HTTP {e.response.status_code} error from auditor agent{error_text}"
        }
    except Exception as e:
        logger.error(f"Unexpected error communicating with auditor agent: {e}")
        logger.debug(f"Exception details:", exc_info=True)
        return {
            "success": False,
            "error": f"Communication failed: {str(e)}",
            "agent_response": f"Failed to communicate with auditor agent: {str(e)}"
        }


async def call_auditor_agent_a2a_framework(message: str, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Call auditor agent using proper A2A framework with A2aMessageBuilder.
    This is the recommended approach based on the shopping agent pattern.
    """
    if not A2A_FRAMEWORK_AVAILABLE:
        logger.warning("A2A Framework not available, skipping this approach")
        return {
            "success": False,
            "error": "A2A Framework not available",
            "agent_response": "A2A Framework components are not available on this system"
        }
        
    if not auditor_agent_client:
        logger.warning("A2A client not initialized, skipping this approach")
        return {
            "success": False,
            "error": "A2A client not initialized", 
            "agent_response": "A2A client could not be initialized"
        }
    
    try:
        logger.info(f"Sending A2A framework message to auditor agent: {message[:100]}...")
        
        # Build A2A message using the framework
        context_id = f"audit_context_{uuid.uuid4().hex[:8]}"
        
        a2a_message = (
            A2aMessageBuilder()
            .set_context_id(context_id)
            .add_text(message)
            .add_data("user_id", user_id)
            .add_data("audit_request_type", "general")
            .build()
        )
        
        logger.debug(f"A2A Framework message built: {a2a_message}")
        
        # Send using the A2A client
        task = await auditor_agent_client.send_a2a_message(a2a_message)
        
        logger.info(f"A2A Framework task submitted: {task}")
        
        # Wait for response (this might need adjustment based on task API)
        response = await task.get_response()  # This API might be different
        
        logger.info(f"✅ A2A Framework SUCCESS! Response: {response}")
        
        # Parse framework response
        if hasattr(response, 'text'):
            agent_response = response.text
        elif hasattr(response, 'content'):
            agent_response = response.content
        else:
            agent_response = str(response)
            
        tool_results = getattr(response, 'tool_results', getattr(response, 'data', []))
        
        return {
            "success": True,
            "agent_response": agent_response,
            "tool_results": tool_results,
            "agent_status": "completed",
            "framework": "A2A",
            "context_id": context_id,
            "raw_result": response
        }
        
    except Exception as e:
        logger.error(f"A2A Framework communication error: {e}")
        logger.debug("A2A Framework error details:", exc_info=True)
        return {
            "success": False,
            "error": f"A2A Framework failed: {str(e)}",
            "agent_response": f"A2A Framework communication failed: {str(e)}"
        }


class AuditRequest(BaseModel):
    """Request model for audit operations."""
    message: str
    audit_type: Optional[str] = None  # "verify_payment", "get_history", "test_integrity"
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None  
    mandate_id: Optional[str] = None
    user_id: str = "default_user"
    session_id: str = "default_session"


class AuditResponse(BaseModel):
    """Response model from auditor interactions."""
    response: str
    agent_name: str = "auditor_agent"
    success: bool
    session_id: str
    audit_data: Optional[Dict] = None  # Structured audit results


@router.get("/health")
async def get_auditor_health():
    """Check the health of the auditor agent."""
    status = agents_manager.get_status()
    
    # Find auditor agent specifically
    auditor_status = None
    for agent in status.get("agents", []):
        if agent.get("name") == "auditor_agent":
            auditor_status = agent
            break
    
    return {
        "status": "healthy" if auditor_status and auditor_status.get("running") else "degraded", 
        "auditor_agent": auditor_status,
        "service": "auditor"
    }


@router.post("/chat")
async def auditor_chat(request: AuditRequest) -> Dict[str, Any]:
    """
    Handle audit requests through the A2A protocol.
    
    This endpoint provides a RESTful interface to the auditor agent,
    which can verify payments, get mandate history, and test ledger integrity.
    
    Examples:
    - "Verify payment PAY_12345"
    - "Show me the history for transaction TXN_67890"
    - "Try to delete payment PAY_12345" (tests immutability)
    """
    try:
        # Check if auditor agent is running
        status = agents_manager.get_status()
        auditor_running = False
        for agent in status.get("agents", []):
            if agent.get("name") == "auditor_agent" and agent.get("running"):
                auditor_running = True
                break
        
        if not auditor_running:
            raise HTTPException(
                status_code=503,
                detail="Auditor agent is not running"
            )
        
        # Call the auditor agent via A2A protocol
        logger.info(f"Processing audit request: {request.message}")
        
        # Try A2A Framework first (if available)
        if A2A_FRAMEWORK_AVAILABLE:
            logger.info("Attempting A2A Framework communication...")
            a2a_result = await call_auditor_agent_a2a_framework(
                message=request.message,
                user_id=request.user_id
            )
            
            if a2a_result["success"]:
                logger.info("✅ A2A Framework communication succeeded!")
            else:
                logger.warning("A2A Framework failed, falling back to JSON-RPC...")
        else:
            logger.info("A2A Framework not available, using JSON-RPC directly...")
            a2a_result = {"success": False}  # Skip A2A Framework
        
        # If A2A Framework fails or is not available, fallback to JSON-RPC
        if not a2a_result["success"]:
            logger.info("Using JSON-RPC A2A communication...")
            a2a_result = await call_auditor_agent_a2a(
                message=request.message,
                user_id=request.user_id
            )
        
        if not a2a_result["success"]:
            # Both approaches failed
            logger.error("All A2A communication methods failed")
            return {
                "response": f"Failed to communicate with auditor agent: {a2a_result['error']}",
                "agent_name": "auditor_agent",
                "success": False,
                "session_id": request.session_id,
                "user_id": request.user_id,
                "error": a2a_result["error"],
                "debug": "All A2A communication methods failed"
            }
        
        # Extract structured audit data from tool results
        tool_results = a2a_result.get("tool_results", [])
        audit_data = None
        
        # Process tool results to extract structured data
        if tool_results:
            # If there are tool results, extract the most relevant one
            audit_data = tool_results[-1] if isinstance(tool_results, list) else tool_results
        
        # Build successful response with actual agent data
        response = {
            "response": a2a_result["agent_response"],
            "agent_name": "auditor_agent",
            "success": True,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "audit_type": request.audit_type,
            "identifiers": {
                "payment_id": request.payment_id,
                "transaction_id": request.transaction_id,
                "mandate_id": request.mandate_id
            },
            "audit_data": audit_data,
            "tool_results_count": len(tool_results) if isinstance(tool_results, list) else 1 if tool_results else 0
        }
        
        logger.info(f"Successfully processed audit request for user {request.user_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing audit request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-payment")
async def verify_payment(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Verify a specific payment by ID.
    
    Convenience endpoint for payment verification.
    Request body: {"payment_id": "PAY_12345", "user_id": "user123"}
    """
    payment_id = request.get("payment_id")
    user_id = request.get("user_id", "default_user")
    
    if not payment_id:
        raise HTTPException(
            status_code=400,
            detail="payment_id is required"
        )
    
    audit_request = AuditRequest(
        message=f"Verify payment {payment_id}",
        audit_type="verify_payment", 
        payment_id=payment_id,
        user_id=user_id
    )
    return await auditor_chat(audit_request)


@router.post("/get-history")
async def get_mandate_history(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Get mandate history and audit trail.
    
    Request body: 
    {"transaction_id": "TXN_12345", "user_id": "user123"} 
    OR 
    {"mandate_id": "MND_67890", "user_id": "user123"}
    """
    transaction_id = request.get("transaction_id")
    mandate_id = request.get("mandate_id")
    user_id = request.get("user_id", "default_user")
    
    if not transaction_id and not mandate_id:
        raise HTTPException(
            status_code=400,
            detail="Either transaction_id or mandate_id must be provided"
        )
    
    message = f"Get history for {'transaction ' + transaction_id if transaction_id else 'mandate ' + mandate_id}"
    
    audit_request = AuditRequest(
        message=message,
        audit_type="get_history",
        transaction_id=transaction_id,
        mandate_id=mandate_id, 
        user_id=user_id
    )
    return await auditor_chat(audit_request)


@router.post("/test-integrity")
async def test_integrity(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Test the immutability of the mandate ledger.
    
    Request body: {
        "identifier": "PAY_12345",
        "operation": "delete", 
        "details": "change amount to $60",  // optional
        "user_id": "user123"
    }
    
    This endpoint demonstrates that the ledger rejects prohibited operations
    like deleting or modifying existing records.
    """
    identifier = request.get("identifier")
    operation = request.get("operation")
    details = request.get("details")
    user_id = request.get("user_id", "default_user")
    
    if not identifier or not operation:
        raise HTTPException(
            status_code=400,
            detail="Both identifier and operation are required"
        )
    
    if operation not in ["delete", "update", "modify"]:
        raise HTTPException(
            status_code=400,
            detail="Operation must be one of: delete, update, modify"
        )
    
    message = f"Try to {operation} {identifier}"
    if details:
        message += f" - {details}"
    
    audit_request = AuditRequest(
        message=message,
        audit_type="test_integrity",
        payment_id=identifier,  # Could be payment_id, transaction_id, or mandate_id
        user_id=user_id
    )
    return await auditor_chat(audit_request)


@router.get("/")
async def auditor_root():
    """Auditor service root endpoint.""" 
    status = agents_manager.get_status()
    auditor_running = any(
        agent.get("name") == "auditor_agent" and agent.get("running") 
        for agent in status.get("agents", [])
    )
    
    return {
        "service": "auditor",
        "version": "1.0.0",
        "description": "A2A Agent Auditor Service - Payment verification and ledger integrity",
        "auditor_healthy": auditor_running,
        "capabilities": [
            "verify_payment", 
            "get_mandate_history",
            "test_ledger_integrity"
        ]
    }