import httpx
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/mandate-ledger", tags=["mandate-ledger"])

@router.get("/health")
async def get_mandate_ledger_health():
    """Forward health check request to mandate ledger service"""
    try:
        # Get mandate ledger service URL from environment
        mandate_ledger_url = os.getenv("MANDATE_LEDGER_SERVICE_URL")
        
        # If no mandate ledger service URL is configured, return mock response
        if not mandate_ledger_url:
            return {
                "status": "healthy",
                "service": "mandate-ledger-mock",
                "message": "Mandate ledger service is running (mock response for demo)",
                "mock": True
            }
        
        # Make request to actual mandate ledger service (if configured)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{mandate_ledger_url}/api/v1/health")
            response.raise_for_status()
            
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to connect to mandate ledger service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )