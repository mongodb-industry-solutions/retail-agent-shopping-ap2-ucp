import { NextResponse } from "next/server";

export async function GET() {
  try {
    console.log('[API Proxy] Received request for mandate ledger service health check');
    // Backend URL - uses loopback when in Kanopy pod
    // Falls back to external URL for local development
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_ENDPOINT || 'http://localhost:8000';

    // Forward request to backend sidecar for mandate ledger health
    const response = await fetch(`${backendUrl}/api/v1/mandate-ledger/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Check if backend responded successfully
    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      return NextResponse.json(
        { 
          error: 'Backend request failed',
          status: response.status,
          statusText: response.statusText
        },
        { status: response.status }
      );
    }
    
    // Get response data from backend
    const data = await response.json();
    
    console.log('[API Proxy] Mandate Ledger health response received:', {...data});
    
    // Return backend response to browser
    return NextResponse.json(data, { status: 200 });
    
  } catch (error) {
    console.error('[API Proxy] Error connecting to mandate ledger service:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to connect to mandate ledger service',
        details: error.message,
        backendUrl: process.env.NEXT_PUBLIC_BACKEND_ENDPOINT
      },
      { status: 500 }
    );
  }
}