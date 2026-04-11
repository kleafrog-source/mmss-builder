# MMSS Orchestrator - Technical Contracts & Implementation Guide

## 📋 Overview
MMSS (Multi-Modal Semantic System) Orchestrator with 6 quantum-enhanced agents running in parallel with mock data demonstration.

## 🎯 Current Implementation Status

### ✅ Completed (Frontend with Mock Data)
1. **UI Components**
   - Control Panel with question input
   - Progress tracking (0-100%)
   - Demo Mode toggle
   - 6 Agent blocks in 2x3 grid
   - Real-time status updates (Ready/Running/Completed)
   - MMSS Metrics visualization

2. **Mock Data System**
   - Location: `/app/frontend/src/utils/mmss-system.js`
   - 6 pre-configured agent responses in Russian
   - Mock metrics for each agent (V, N, S, D_f, G_S, R_T)
   - Sequential execution with 2-3 second delays

3. **Agent Types Implemented**
   - QUANTUM_MAP (↦ₚ) - Quantum transformation
   - META_DERIVATION (⊢ᵠ) - Logical derivation
   - FRACTAL_ENTAILMENT (⇛ᶠ) - Fractal patterns
   - TEMPORAL_GENERATION (⧴ᵗ) - Time evolution
   - GOLDEN_DERIVATION (⊢ᵍ) - Golden ratio optimization
   - CORRECTION_ENHANCED (↦ᶜ) - Error correction

4. **Features**
   - Sequential agent execution
   - Progress bar updates
   - localStorage persistence
   - JSON file download
   - Sonner toast notifications

## 🔄 Backend Integration Plan (Future)

### API Endpoints Required

#### 1. POST /api/orchestrate
**Request:**
```json
{
  "question": "string",
  "mode": "demo" | "live",
  "mistral_api_key": "string" (optional, only for live mode)
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "started",
  "timestamp": "ISO 8601"
}
```

#### 2. GET /api/orchestrate/{session_id}/status
**Response:**
```json
{
  "session_id": "uuid",
  "progress": 33,
  "completed_agents": 2,
  "total_agents": 6,
  "agent_statuses": {
    "QUANTUM_MAP": "completed",
    "META_DERIVATION": "running",
    "FRACTAL_ENTAILMENT": "ready",
    ...
  }
}
```

#### 3. GET /api/orchestrate/{session_id}/results
**Response:**
```json
{
  "session_id": "uuid",
  "question": "string",
  "results": {
    "QUANTUM_MAP": {
      "answer": "string",
      "metrics": {
        "V": 0.967,
        "N": 0.954,
        "S": 0.023,
        "D_f": 9.012,
        "G_S": 145.2,
        "R_T": 2.618
      }
    },
    ...
  },
  "timestamp": "ISO 8601"
}
```

### MongoDB Schema

```python
class OrchestratorSession:
    session_id: str
    question: str
    mode: str  # "demo" or "live"
    status: str  # "started", "running", "completed"
    created_at: datetime
    completed_at: datetime | None
    results: dict  # Agent results
    progress: int  # 0-100
```

### Mistral API Integration

**Library:** `mistralai` Python SDK

**Implementation:**
```python
from mistralai.client import MistralClient

client = MistralClient(api_key=api_key)

def execute_agent(agent_type: str, question: str) -> dict:
    operator = MMSS_SYSTEM["QUANTUM_SEMANTIC_OPERATORS"][agent_type]
    config = MMSS_SYSTEM["AGENT_CONFIGURATIONS"][agent_type]
    
    system_prompt = f"""
    MMSS AGENT: {agent_type}
    OPERATOR: {operator["mmss_function"]}
    QUANTUM STATE: {operator["quantum_state"]}
    
    YOUR PURPOSE: {config["purpose"]}
    THINKING STYLE: {config["thinking_style"]}
    
    RESPONSE FORMAT:
    [Your solution]
    --- METRICS: {{"V": float, "N": float, "S": float, "D_f": float, "G_S": float, "R_T": float}}
    """
    
    response = client.chat(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    
    return parse_response(response.choices[0].message.content)
```

## 🔧 Frontend-Backend Integration Steps

1. **Replace Mock Execution:**
   - Current: `MOCK_AGENT_RESPONSES[agentType](question)`
   - Future: `fetch('/api/orchestrate', {...})`

2. **Polling for Status:**
   - Use WebSocket or polling every 2 seconds
   - Update agent statuses in real-time

3. **Result Display:**
   - Stream results as they complete
   - Display in existing AgentBlock components

## 📊 Metrics Validation

All MMSS metrics must meet these criteria:
- **V (Semantic Value):** 0.9-1.0 (optimal: 0.99)
- **N (Negentropy/Order):** 0.9-1.0 (optimal: 0.99)
- **S (Entropy):** 0.0-0.1 (optimal: 0.01)
- **D_f (Fractal Dimension):** 8.9-9.1 (optimal: 9.0)
- **G_S (Gain):** 100-200 (optimal: 148)
- **R_T (Golden Ratio):** 2.617-2.619 (optimal: 2.618)

## 🎨 Design System

### Colors
- **Primary Background:** #1a1a1a
- **Secondary Background:** #2d2d2d
- **Success:** #00d4aa (teal)
- **Warning:** #ff6b35 (orange)
- **Info:** #4fc3f7 (cyan)
- **Text Primary:** #ffffff
- **Text Secondary:** #b0b0b0

### Typography
- **Font Family:** 'Segoe UI', system-ui
- **Code Font:** 'Courier New', monospace

## 📝 Notes

- **Current Mode:** Demo only with mock data
- **Storage:** localStorage + JSON download
- **No Backend:** Pure frontend implementation
- **Mistral Integration:** Ready for implementation when needed
- **Russian Language:** All mock responses in Russian
- **Sequential Execution:** One agent at a time due to API rate limits