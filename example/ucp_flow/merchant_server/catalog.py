# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
UCP Product Catalog Endpoints.

This module provides product search functionality via UCP REST API.
The LLM-based product generation is reused from the card_flow catalog_agent.
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai

from ap2.types.payment_request import PaymentItem, PaymentCurrencyAmount

router = APIRouter(tags=["Catalog"])
logger = logging.getLogger(__name__)


class ProductSearchRequest(BaseModel):
    """Request for product search."""
    query: str
    max_results: Optional[int] = 3


class ProductSearchResponse(BaseModel):
    """Response containing matching products."""
    products: list[PaymentItem]
    query: str


@router.get("/products")
async def search_products(
    q: str,
    max_results: int = 3
) -> ProductSearchResponse:
    """
    Search for products matching a query.
    
    This endpoint uses Gemini to generate realistic product options
    based on the user's natural language query.
    
    Args:
        q: Natural language search query (e.g., "coffee maker")
        max_results: Maximum number of products to return (default: 3)
    
    Returns:
        List of matching products with prices
    """
    logger.info(f"Product search: '{q}' (max: {max_results})")
    
    try:
        llm_client = genai.Client()
        
        prompt = f"""
        Based on the user's request for '{q}', generate {max_results} 
        complete, unique and realistic product options.
        
        For each product:
        - Create a descriptive label (product name and key features)
        - Set a realistic USD price
        - Include a 30-day refund period
        
        Do NOT include brand names in the label.
        """
        
        llm_response = llm_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[PaymentItem],
            }
        )
        
        products = llm_response.parsed
        logger.info(f"Generated {len(products)} products for query: '{q}'")
        
        return ProductSearchResponse(
            products=products,
            query=q
        )
        
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search products: {str(e)}"
        )


@router.post("/products/search")
async def search_products_post(request: ProductSearchRequest) -> ProductSearchResponse:
    """
    Search for products (POST version for complex queries).
    """
    return await search_products(
        q=request.query,
        max_results=request.max_results or 3
    )

