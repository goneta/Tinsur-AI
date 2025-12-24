import { NextRequest } from "next/server";

interface PerksSnapshotData {
  activities: string[];
  partners: string[];
  insights: string;
}

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
  try {
    const { userId } = await request.json();
    console.log(
      "[ADK API] 🚀 Starting perks snapshot request for userId:",
      userId
    );

    if (!userId) {
      console.log("[ADK API] ❌ No userId provided");
      return Response.json({ error: "User ID is required" }, { status: 400 });
    }

    // 1. Create ADK session for the perks_snapshot_agent agent
    const sessionUrl = `http://localhost:8082/apps/perks_snapshot_agent/users/${userId}/sessions`;
    const sessionRequestBody = { state: {} };

    console.log("[ADK API] 📡 Creating ADK session...");
    console.log("[ADK API] 📡 Session URL:", sessionUrl);
    console.log(
      "[ADK API] 📡 Session request body:",
      JSON.stringify(sessionRequestBody, null, 2)
    );

    const sessionResponse = await fetch(sessionUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sessionRequestBody),
    });

    console.log(
      "[ADK API] 📡 Session response status:",
      sessionResponse.status
    );
    console.log(
      "[ADK API] 📡 Session response headers:",
      Object.fromEntries(sessionResponse.headers.entries())
    );

    if (!sessionResponse.ok) {
      console.log(
        "[ADK API] ❌ Session creation failed with status:",
        sessionResponse.status
      );
      const errorText = await sessionResponse.text();
      console.log("[ADK API] ❌ Session error response:", errorText);
      throw new Error(
        `Failed to create ADK session: ${sessionResponse.status} - ${errorText}`
      );
    }

    const session: ADKSessionResponse = await sessionResponse.json();
    console.log("[ADK API] ✅ Session created successfully:");
    console.log("[ADK API] ✅ Session data:", JSON.stringify(session, null, 2));

    // 2. Send message to perks_snapshot_agent agent to get perks summary
    const agentRequest: ADKAgentRequest = {
      app_name: "perks_snapshot_agent",
      user_id: userId,
      session_id: session.id,
      new_message: {
        role: "user",
        parts: [{ text: `Get perks summary for ${userId}` }],
      },
      streaming: false,
    };

    console.log("[ADK API] 🤖 Sending request to perks agent...");
    console.log("[ADK API] 🤖 Agent request URL: http://localhost:8082/run");
    console.log(
      "[ADK API] 🤖 Agent request body:",
      JSON.stringify(agentRequest, null, 2)
    );

    const agentResponse = await fetch(`http://localhost:8082/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(agentRequest),
    });

    console.log("[ADK API] 🤖 Agent response status:", agentResponse.status);
    console.log(
      "[ADK API] 🤖 Agent response headers:",
      Object.fromEntries(agentResponse.headers.entries())
    );

    if (!agentResponse.ok) {
      console.log(
        "[ADK API] ❌ Agent request failed with status:",
        agentResponse.status
      );
      const errorText = await agentResponse.text();
      console.log("[ADK API] ❌ Agent error response:", errorText);
      throw new Error(
        `ADK agent request failed: ${agentResponse.status} - ${errorText}`
      );
    }

    const agentData = await agentResponse.json();
    console.log("[ADK API] 🤖 Raw agent response received:");
    console.log("[ADK API] 🤖 Agent data type:", typeof agentData);
    console.log(
      "[ADK API] 🤖 Agent data keys:",
      agentData ? Object.keys(agentData) : "no keys"
    );
    console.log(
      "[ADK API] 🤖 Full agent response:",
      JSON.stringify(agentData, null, 2)
    );

    // 3. Parse and transform the response to expected format
    console.log("[ADK API] 🔄 Parsing ADK agent workflow array...");
    console.log("[ADK API] 🔄 Agent data is array:", Array.isArray(agentData));
    console.log("[ADK API] 🔄 Agent data length:", agentData?.length);

    if (!Array.isArray(agentData) || agentData.length === 0) {
      throw new Error("Invalid agent response format - expected array");
    }

    // Get the last element in the workflow array (final result)
    const finalStep = agentData[agentData.length - 1];
    console.log(
      "[ADK API] 🎯 Final workflow step:",
      JSON.stringify(finalStep, null, 2)
    );

    // Extract the JSON string from content.parts[0].text
    const contentParts = finalStep?.content?.parts;
    if (
      !contentParts ||
      !Array.isArray(contentParts) ||
      contentParts.length === 0
    ) {
      throw new Error("No content parts found in final step");
    }

    const finalText = contentParts[0]?.text;
    if (!finalText) {
      throw new Error("No text content found in final step");
    }

    console.log("[ADK API] 📝 Final text content:", finalText);

    // Parse the JSON string
    let parsedData;
    try {
      parsedData = JSON.parse(finalText);
      console.log("[ADK API] ✅ Parsed JSON successfully:", parsedData);
    } catch (parseError) {
      console.error("[ADK API] ❌ JSON parse error:", parseError);
      throw new Error(`Failed to parse agent response JSON: ${parseError}`);
    }

    const perksData: PerksSnapshotData = {
      activities: parsedData.activities || [],
      partners: parsedData.partners || [],
      insights: parsedData.insights || "",
    };

    console.log("[ADK API] ✅ Final transformed data:");
    console.log(
      "[ADK API] ✅ Transformed data:",
      JSON.stringify(perksData, null, 2)
    );
    console.log("[ADK API] ✅ Returning success response to frontend");

    return Response.json(perksData);
  } catch (error) {
    console.error("[ADK API] ❌ ERROR in perks snapshot API:", error);
    console.error("[ADK API] ❌ Error type:", typeof error);
    console.error(
      "[ADK API] ❌ Error message:",
      error instanceof Error ? error.message : "Unknown error"
    );
    console.error(
      "[ADK API] ❌ Error stack:",
      error instanceof Error ? error.stack : "No stack trace"
    );

    return Response.json(
      {
        error: "Failed to fetch perks data",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
