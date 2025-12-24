# ADK Server API Endpoints Documentation

## Overview

The `adk server_api` (also referred to as `adk api_server`) command creates a **FastAPI web server** that exposes your ADK agents through RESTful API endpoints. This server enables you to test your agents by sending cURL commands or API requests.

## Starting the Server

```bash
# Basic server start
adk api_server

# Java version with custom port
mvn compile exec:java \
     -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"

# A2A server with specific port
adk api_server --a2a --port 8001 path/to/agent --log_level debug
```

## Core Agent Execution Endpoints

### **Agent Operations**
- **`GET /list-apps`** - Lists all available agent applications
  ```bash
  curl -X GET http://localhost:8000/list-apps
  ```
  Response: `["my_sample_agent", "another_agent"]`

- **`POST /run`** - Executes an agent run (non-streaming)
- **`POST /run-sse`** - Executes an agent run with Server-Sent Events (streaming)
  ```bash
  curl -X POST http://localhost:8000/run_sse \
    -H "Content-Type: application/json" \
    -d '{
      "app_name": "my_agent",
      "user_id": "user_123", 
      "session_id": "session_abc",
      "new_message": {
        "role": "user",
        "parts": [{"text": "Hello, agent!"}]
      },
      "streaming": false
    }'
  ```

## Session Management Endpoints

### **Session CRUD Operations**
- **`POST /apps/{appName}/users/{userId}/sessions/{sessionId}`** - Creates or updates a session with specific ID
  ```bash
  curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
    -H "Content-Type: application/json" \
    -d '{"state": {"visit_count": 5}}'
  ```
  Response: `{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[],"lastUpdateTime":1743711430.022186}`

- **`POST /apps/{appName}/users/{userId}/sessions`** - Creates a session with auto-generated ID
- **`GET /apps/{appName}/users/{userId}/sessions/{sessionId}`** - Retrieves session details
  ```bash
  curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
  ```

- **`GET /apps/{appName}/users/{userId}/sessions`** - Lists all sessions for a user
- **`DELETE /apps/{appName}/users/{userId}/sessions/{sessionId}`** - Deletes a session
  ```bash
  curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
  ```
  Response: `204 No Content` on successful deletion

## Artifact Management Endpoints

### **Artifact Operations**
- **`GET /apps/{appName}/users/{userId}/sessions/{sessionId}/artifacts`** - Lists all artifact names for a session
- **`GET /apps/{appName}/users/{userId}/sessions/{sessionId}/artifacts/{artifactName}`** - Gets latest version of an artifact
  - Optional query parameter: `version` - Specific version number
- **`GET /apps/{appName}/users/{userId}/sessions/{sessionId}/artifacts/{artifactName}/versions/{versionId}`** - Gets specific artifact version

## Debugging & Tracing Endpoints

### **OpenTelemetry Integration**
- **`GET /debug/trace/{eventId}`** - Retrieves trace information by event ID (gcp.vertex.agent.event_id)
- **`GET /debug/trace/session/{sessionId}`** - Gets trace spans for a session
- **`GET /apps/{appName}/users/{userId}/sessions/{sessionId}/events/{eventId}/graph`** - Gets graph representation of an event

## Evaluation Endpoints (Stub/Placeholder)

### **Evaluation Set Management**
- **`POST /apps/{appName}/eval-sets/{evalSetId}/add-session`** - Adds session to evaluation set
- **`POST /apps/{appName}/eval-sets/{evalSetId}/run-eval`** - Runs evaluations
- **`GET /apps/{appName}/eval-results`** - Lists evaluation results (returns empty list - not implemented)
- **`GET /apps/{appName}/eval-results/{evalResultId}`** - Gets specific evaluation result (not implemented)

## Streaming Endpoints

### **Real-time Communication**
- **WebSocket `/run_live`** - WebSocket endpoint for live communication
- **Server-Sent Events** - All API endpoints can emit SSE for streaming responses

## Authentication & Headers

### **Cloud Run Deployment**
```bash
# Get authentication token
export TOKEN=$(gcloud auth print-identity-token)

# Use with requests
curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
```

### **GKE Deployment**
```bash
# Get service URL
export APP_URL=$(kubectl get service adk-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

## Development Features

### **Dev UI**
- **`GET /dev-ui`** - Web interface for agent interaction (root `/` redirects here)
- Static content served from directory specified by `adk.web.ui.dir` system property

### **Configuration**
- **CORS Support** - Configurable cross-origin requests
- **Resource Handlers** - Serves static content like Dev UI
- **View Controllers** - Handles routing and redirects

## AgentController Class Methods

The ADK web server uses Spring Boot and provides the following controller methods:

```java
// Agent execution
agentRun(AgentRunRequest request): List<Event>
agentRunSse(AgentRunRequest request): SseEmitter

// Session management
createSession(String appName, String userId, Map<String, Object> state): Session
createSessionWithId(String appName, String userId, String sessionId, Map<String, Object> state): ResponseEntity<Void>
getSession(String appName, String userId, String sessionId): Session
listSessions(String appName, String userId): List<Session>
deleteSession(String appName, String userId, String sessionId): ResponseEntity<Object>

// Artifact management
loadArtifact(String appName, String userId, String sessionId, String artifactName, Integer version): Part
loadArtifactVersion(String appName, String userId, String sessionId, String artifactName, int versionId): Part
listArtifactNames(String appName, String userId, String sessionId): List<String>

// Debug and tracing
getTraceDict(String eventId): ResponseEntity<?>
getSessionTrace(String sessionId): ResponseEntity<Object>
getEventGraph(String appName, String userId, String sessionId, String eventId): ResponseEntity<GraphResponse>

// Application management
listApps(): List<String>
```

## Example Full Workflow

```bash
# 1. Start the server
adk api_server

# 2. List available agents
curl -X GET http://localhost:8000/list-apps

# 3. Create a session
curl -X POST http://localhost:8000/apps/my_agent/users/user_123/sessions/session_abc \
  -H "Content-Type: application/json" \
  -d '{"state": {"preferred_language": "English", "visit_count": 5}}'

# 4. Send a message to the agent
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_agent",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
      "role": "user",
      "parts": [{
        "text": "What is the capital of Canada?"
      }]
    },
    "streaming": false
  }'

# 5. Get session details
curl -X GET http://localhost:8000/apps/my_agent/users/user_123/sessions/session_abc

# 6. List artifacts if any were created
curl -X GET http://localhost:8000/apps/my_agent/users/user_123/sessions/session_abc/artifacts
```

## Transport Protocol

- **Transport**: All API endpoints emit Server‑Sent Events (SSE)
- **Streaming**: ADK event JSON envelopes on `data:` lines
- **Content**: Clients parse `content.parts` and `actions.stateDelta`
- **Progress**: Snapshots stream progress envelopes and final blocks payload
- **Chat**: Streams incremental text via `content.parts[].text` across frames

## Notes

- The specific endpoints available depend on your agent configuration and custom tools
- The server automatically discovers and exposes agents based on the agent registry
- Default port is typically 8000 but can be configured
- Java version bundles Dev UI and API server together
- OpenTelemetry integration provides automatic tracing and observability
