import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const body = await request.json();
    const { workflowId, conversation = [] } = body;

    // Validate required fields
    if (!workflowId) {
      return NextResponse.json(
        { error: "Missing required field: workflowId" },
        { status: 400 },
      );
    }

    return NextResponse.json({
      workflowId: "straightforward",
      stepId: "shopping-agent-introduction",
      answers: [
        "I'm looking for a coffee maker, specifically a glass French press. I don't have a preferred merchant, but I'd like it to be refundable. Show me some options.",
        "I'm looking for gaming headphones with noise cancellation. They don't need to be refundable, but I'd like them from the merchant Amazon. Show me some options.",
      ],
    });

    const backendUrl =
      process.env.NEXT_PUBLIC_ASSISTANT_ENDPOINT || "http://localhost:8005";

    const response = await fetch(`${backendUrl}`, {
      // TODO UPDATE
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        workflowId,
        conversation,
      }),
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
