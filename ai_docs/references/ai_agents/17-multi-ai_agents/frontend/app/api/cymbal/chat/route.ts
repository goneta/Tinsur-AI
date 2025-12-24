import { NextRequest } from "next/server";

interface ADKSessionResponse {
  id: string;
  appName: string;
  userId: string;
  state: Record<string, unknown>;
  events: unknown[];
  lastUpdateTime: number;
}

interface ADKAgentRequest {
  app_name: string;
  user_id: string;
  session_id: string;
  new_message: {
    role: string;
    parts: Array<{ text: string }>;
  };
  streaming: boolean;
}

export async function POST(request: NextRequest): Promise<Response> {
  console.log("[ADK CHAT] 🚀 Starting chat request...");

  try {
    const {
      userId,
      message,
      sessionId,
      topic = "spending",
    } = await request.json();
    console.log("[ADK CHAT] 📋 Request data:", {
      userId,
      message,
      topic,
      hasSessionId: !!sessionId,
    });

    if (!userId) {
      return Response.json({ error: "User ID is required" }, { status: 400 });
    }

    if (!message) {
      return Response.json({ error: "Message is required" }, { status: 400 });
    }

    let currentSessionId = sessionId;

    // If no session provided, create new session (simple - no context fetching)
    if (!currentSessionId) {
      console.log("[ADK CHAT] 🆕 Creating new ADK chat session...");

      try {
        // Create session with simple initial state (context comes from frontend message)
        const sessionState = {
          topic: topic,
          user_id: userId,
        };

        console.log("[ADK CHAT] 📡 Creating session with state:", sessionState);

        const sessionResponse = await fetch(
          `http://localhost:8090/apps/chat/users/${userId}/sessions`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ state: sessionState }),
          }
        );

        if (!sessionResponse.ok) {
          throw new Error(
            `Failed to create ADK session: ${sessionResponse.status}`
          );
        }

        const session: ADKSessionResponse = await sessionResponse.json();
        currentSessionId = session.id;

        console.log("[ADK CHAT] ✅ ADK session created:", currentSessionId);
        console.log("[ADK CHAT] 📋 Session details:", {
          id: session.id,
          appName: session.appName,
          userId: session.userId,
          stateKeys: Object.keys(session.state),
        });
      } catch (sessionError) {
        console.error("[ADK CHAT] ❌ Session creation failed:", sessionError);
        throw new Error("Failed to create chat session");
      }
    } else {
      console.log("[ADK CHAT] 🔄 Using existing session:", currentSessionId);
    }

    // Send message to ADK agent (simple JSON request)
    console.log("[ADK CHAT] 🤖 Sending message to ADK agent...");
    const agentRequest: ADKAgentRequest = {
      app_name: "chat",
      user_id: userId,
      session_id: currentSessionId,
      new_message: {
        role: "user",
        parts: [{ text: message }],
      },
      streaming: false, // Use simple JSON response instead of streaming
    };

    console.log("[ADK CHAT] 📡 Agent request details:", {
      app_name: agentRequest.app_name,
      user_id: agentRequest.user_id,
      session_id: agentRequest.session_id,
      message_preview: message.substring(0, 50),
      streaming: agentRequest.streaming,
    });

    const agentResponse = await fetch(`http://localhost:8090/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(agentRequest),
    });

    console.log("[ADK CHAT] ✅ ADK agent response received");
    console.log("[ADK CHAT] 📥 Agent response:", agentResponse);

    if (!agentResponse.ok) {
      throw new Error(`ADK agent request failed: ${agentResponse.status}`);
    }

    const agentData = await agentResponse.json();

    // Debug: ADK returns an array of events, not a single object
    console.log("[ADK CHAT] 📥 Response is array:", Array.isArray(agentData));
    console.log(
      "[ADK CHAT] 📥 Response length:",
      Array.isArray(agentData) ? agentData.length : "N/A"
    );
    console.log("[ADK CHAT] 📥 Agent response structure:", {
      isArray: Array.isArray(agentData),
      length: Array.isArray(agentData) ? agentData.length : 0,
      hasContent: !!agentData.content, // Will be false if it's an array
      firstItemKeys:
        Array.isArray(agentData) && agentData.length > 0
          ? Object.keys(agentData[0])
          : [],
    });

    // Extract text content from the response - ADK returns array of events
    let responseText = "";

    if (Array.isArray(agentData)) {
      // ADK returns array of events - find the final response with text
      console.log(
        "[ADK CHAT] 🔍 Processing array of",
        agentData.length,
        "events"
      );

      // Iterate through all events and collect text responses (usually the last one is the final answer)
      for (let i = 0; i < agentData.length; i++) {
        const event = agentData[i];
        if (event.content?.parts) {
          for (const part of event.content.parts) {
            if (part.text) {
              responseText += part.text; // Accumulate all text responses
              console.log(
                "[ADK CHAT] 📝 Found text in event",
                i,
                ":",
                part.text.substring(0, 50) + "..."
              );
            }
          }
        }
      }
    } else {
      // Fallback: Handle single object response (legacy format)
      if (agentData.content?.parts) {
        for (const part of agentData.content.parts) {
          if (part.text) {
            responseText += part.text;
          }
        }
      }

      // Try other common fields
      if (!responseText && agentData.text) {
        responseText = agentData.text;
      }
      if (!responseText && agentData.message) {
        responseText = agentData.message;
      }
      if (!responseText && agentData.response) {
        responseText = agentData.response;
      }
    }

    if (!responseText) {
      console.error("[ADK CHAT] ❌ Could not find text in any expected field");
      throw new Error("No text content received from agent");
    }

    console.log(
      "[ADK CHAT] 💬 Found response text:",
      responseText.substring(0, 100) + "..."
    );

    // Return simple JSON response (always include session_id for frontend state management)
    return Response.json({
      response: responseText,
      session_id: currentSessionId, // Always return session_id for persistence
      timestamp: Date.now(),
    });
  } catch (error) {
    console.error("[ADK CHAT] ❌ Chat request error:", error);

    return Response.json(
      {
        error: "Failed to process chat request",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
