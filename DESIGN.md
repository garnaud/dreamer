# Project "Dreamer" - Design Document

## 1. Project Overview
"Dreamer" is a personal AI companion application designed to maintain a continuous, evolving relationship with the user. It acts as a confidant, a memory keeper, and a creative partner.

**Core Philosophy:**
- **Local & Private:** All data (memories, logs) is stored locally.
- **Proactive & Adaptive:** The AI doesn't just reply; it guides the conversation, finds connections in past memories, and adapts to the user's mood.
- **Specialized:** Different "personas" or agents handle specific tasks (dreaming, fact-checking, listening).

## 2. Architecture

We will build a **Client-Server** application to ensure a clean separation between the interface and the intelligent logic.

### High-Level Components:

1.  **Frontend (The "Interface"):**
    *   A minimal, distraction-free Web App.
    *   **Tech Stack:** Next.js (React), Tailwind CSS.
    *   **Features:** Chat stream, history view, "Dream" visualization area.

2.  **Backend (The "Brain"):**
    *   Orchestrates the agents and handles memory.
    *   **Tech Stack:** Python, FastAPI.
    *   **Agent Framework:** LangGraph (ideal for stateful, multi-step agent workflows).

3.  **Memory Core (The "Soul"):**
    *   **Structured Data:** SQLite. Stores user profile, explicit facts (e.g., "Birthday is Jan 1st"), and conversation logs.
    *   **Semantic Data:** ChromaDB (Local Vector Store). Stores embeddings of conversations to retrieve "feelings", "souvenirs", and context based on meaning rather than keywords.

### Agentic Workflow (LangGraph)

Instead of a single bot, we will have a graph of specialized nodes:

*   **Router:** Analyzes the user's input to decide the next step (e.g., "Is this a new memory?", "Does the user need comfort?", "Requesting a dream?").
*   **The Companion (Main Agent):** Handles general empathetic conversation. Queries memory to find connections ("This reminds me of what you said last week...").
*   **The Archivist:** Runs in the background. Extracts entities and saves them to SQLite/Vector DB.
*   **The Dreamer:** Generates creative text-based narratives or "dream sequences" based on retrieved memories to offer new perspectives.
*   **The Fact Checker:** Verifies consistency (e.g., User: "I have 2 brothers." -> Checker: "Wait, you previously mentioned 3 siblings...").

## 3. Data Model & Access

**Direct Access Pattern (No MCP required):**
Agents running in the Python backend will interact with the database directly using **Function Calling**.
- The LLM will have access to defined tools (e.g., `save_memory()`, `search_facts()`).
- When an agent needs information, it invokes these Python functions, which directly query SQLite or ChromaDB.

**1. Facts (SQLite):**
```sql
Table: Facts
- id
- category (Project, Personal, Preference)
- content (e.g., "Working on AI project")
- confidence_score
- last_updated
```

**2. Episodic Memory (ChromaDB):**
- Documents: Chunks of past conversations.
- Metadata: Date, emotional sentiment, tags.

## 4. Implementation Roadmap

### Phase 1: Foundation
- [ ] Initialize Project Structure (Monorepo: `/frontend`, `/backend`).
- [ ] Set up Python environment and LangGraph basics.
- [ ] Set up SQLite and ChromaDB persistence.

### Phase 2: The Brain (Backend)
- [ ] Implement the **Archivist** to save/retrieve memories.
- [ ] Implement the **Companion** loop (Receive -> Recall -> Reason -> Respond).
- [ ] Create a basic FastAPI endpoint to expose this.

### Phase 3: The Face (Frontend)
- [ ] Build the Next.js chat interface.
- [ ] Connect to FastAPI.

### Phase 4: Specialization
- [ ] Add **The Dreamer** agent (Creative writing capabilities).
- [ ] Add **The Fact Checker** (Consistency logic).

## 5. Questions for the User
- Do you want the "Dreamer" to generate images (requiring DALL-E/Stable Diffusion) or just text?
- For local storage, is a simple file-based SQLite/Chroma setup sufficient, or do you strictly need an MCP server implementation?
