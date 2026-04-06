import { NextResponse } from 'next/server'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const session_id = searchParams.get('session_id')
    const user_id = searchParams.get('user_id')

    // Validate required fields
    if (!session_id || !user_id) {
      return NextResponse.json(
        { error: 'Missing required parameters: session_id, user_id' },
        { status: 400 }
      )
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_ENDPOINT || 'http://localhost:8000'
    
    const response = await fetch(
      `${backendUrl}/api/v1/auditor/session/${encodeURIComponent(session_id)}?user_id=${encodeURIComponent(user_id)}`, 
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      }
    )

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Get Auditor Session API error:', error)
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