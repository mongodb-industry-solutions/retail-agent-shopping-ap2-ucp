import httpx
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/mandate-ledger", tags=["mandate-ledger"])

@router.get("/health")
async def get_mandate_ledger_health():
    """Forward health check request to mandate ledger service"""
    try:
        # Get mandate ledger service URL from environment
        mandate_ledger_url = os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000")
        
        # Make request to mandate ledger service
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