import { NextResponse } from 'next/server'

export async function POST(request) {
  try {
    const body = await request.json()
    const { message, user_id, session_id } = body

    // Validate required fields
    if (!message || !user_id || !session_id) {
      return NextResponse.json(
        { error: 'Missing required fields: message, user_id, session_id' },
        { status: 400 }
      )
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_ENDPOINT || 'http://localhost:8000'
    
    const response = await fetch(`${backendUrl}/api/v1/auditor/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id,
        session_id,
        context: {}
      })
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Auditor Chat API error:', error)
    return NextResponse.json(
      { 
        error: 'Failed to connect to backend', 
        details: error.message,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}