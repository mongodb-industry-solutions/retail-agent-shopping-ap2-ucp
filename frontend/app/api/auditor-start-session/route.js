import { NextResponse } from 'next/server'

export async function POST(request) {
  try {
    const { searchParams } = new URL(request.url)
    const user_id = searchParams.get('user_id')
    const body = await request.json()
    const { message } = body

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_ENDPOINT || 'http://localhost:8000'
    const finalUrl = `${backendUrl}/api/v1/auditor/start-session?user_id=${encodeURIComponent(user_id)}&message=${encodeURIComponent(message)}`

    const response = await fetch(finalUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Auditor Start Session API error:', error)
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