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
UCP Merchant Server - FastAPI implementation.

This server implements UCP REST endpoints with AP2 Mandate Ledger integration.
Unlike the A2A-based card_flow, this uses standard REST APIs for shopper-merchant
communication while maintaining the same AP2 ledger writes for audit trail.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from .well_known import router as well_known_router
from .catalog import router as catalog_router
from .checkout import router as checkout_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("=" * 60)
    print("🏪 UCP Merchant Server Starting")
    print("=" * 60)
    print(f"  Ledger URL: {os.getenv('MANDATE_LEDGER_SERVICE_URL', 'http://localhost:5000')}")
    print(f"  API Key: {'✓ Set' if os.getenv('MANDATE_LEDGER_API_KEY') else '✗ Not Set'}")
    print("=" * 60)
    print("  Endpoints:")
    print("    GET  /.well-known/ucp.json  - UCP capability discovery")
    print("    GET  /api/products          - Search products")
    print("    POST /api/checkout          - Create checkout session")
    print("    POST /api/checkout/{id}/confirm - Confirm cart selection")
    print("    POST /api/checkout/{id}/complete - Complete payment")
    print("=" * 60)
    yield
    print("🏪 UCP Merchant Server Shutting Down")


app = FastAPI(
    title="UCP Merchant Server",
    description="UCP-compliant merchant with AP2 Mandate Ledger integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(well_known_router)
app.include_router(catalog_router, prefix="/api")
app.include_router(checkout_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ucp-merchant-server"}

