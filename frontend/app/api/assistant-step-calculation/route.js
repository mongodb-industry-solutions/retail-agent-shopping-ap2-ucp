import { NextResponse } from "next/server";

// Helper function to sanitize MongoDB-specific objects for JSON serialization
function sanitizeMongoDocument(doc) {
  if (!doc) return doc;
  
  const sanitized = JSON.parse(JSON.stringify(doc, (key, value) => {
    // Convert MongoDB ObjectId to string
    if (value && typeof value === 'object' && value.$oid) {
      return value.$oid;
    }
    // Convert MongoDB Date to ISO string
    if (value && typeof value === 'object' && value.$date) {
      return value.$date;
    }
    return value;
  }));
  
  return sanitized;
}

export async function POST(request) {
  try {
    const contentType = request.headers.get('content-type');
    console.log('[ASSISTANT-STEP-CALC] Content-Type:', contentType);
    
    let body;
    try {
      body = await request.json();
      console.log('[ASSISTANT-STEP-CALC] Successfully parsed JSON body');
    } catch (parseError) {
      console.error('[ASSISTANT-STEP-CALC] JSON parse error:', parseError);
      return NextResponse.json(
        { 
          error: "Invalid or empty JSON in request body",
          details: parseError.message,
          hint: "Make sure you're sending a valid JSON body with workflowId"
        },
        { status: 400 }
      );
    }
    
    const { workflowId, conversation = [], maxAnswers = 2, paymentDocument = null } = body;

    // Validate required fields
    if (!workflowId) {
      return NextResponse.json(
        { error: "Missing required field: workflowId" },
        { status: 400 },
      );
    }

    const backendUrl = process.env.ASSISTANT_ENDPOINT || "http://localhost:3333";

    let payload = {
      workflowId,
      conversation,
      maxAnswers,
    };
    
    if (paymentDocument) {
      // Sanitize MongoDB-specific objects for JSON serialization
      const sanitizedPaymentDocument = sanitizeMongoDocument(paymentDocument);
      payload.paymentDocument = sanitizedPaymentDocument;
    }

    console.log('[ASSISTANT-STEP-CALC] Sending payload:', JSON.stringify(payload, null, 2));

    const response = await fetch(`${backendUrl}/api/process`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "accept": "application/json"
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      {
        error: "Failed to connect to backend",
        details: error.message,
        timestamp: new Date().toISOString(),
      },
      { status: 500 },
    );
  }
}