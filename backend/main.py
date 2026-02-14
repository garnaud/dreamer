from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlmodel import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

from database import create_db_and_tables, get_session, engine
from vector_store import add_memory, search_memories
from models import Fact
from archivist import extract_and_save_facts
from dreamer import generate_dream
from interviewer import analyze_gaps_and_ask

load_dotenv()

# Initialize Gemini LLM
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY not found in environment variables. LLM features will fail.")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Dreamer API", lifespan=lifespan)

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def process_background_tasks(user_message: str):
    # Create a new session for the background task to avoid "Session is closed" errors
    with Session(engine) as session:
        extract_and_save_facts(user_message, session)

@app.get("/")
def read_root():
    return {"message": "Dreamer API is running with Gemini LLM"}

@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_session)):
    try:
        # 1. Retrieve related memories (context)
        related_memories = search_memories(request.message, n_results=3)
        context_str = ""
        if related_memories and related_memories['documents']:
            # Flatten the list of lists
            docs = related_memories['documents'][0]
            context_str = "\n".join([f"- {doc}" for doc in docs])

        # 2. Get Interviewer suggestion (a curiosity question)
        # We fetch this every time to keep the AI curious, but instruct it to use it only if relevant or as a follow-up.
        interviewer_question = analyze_gaps_and_ask(db)
        
        # 3. Construct Prompt with Context
        system_prompt = (
            "You are a personal AI companion named 'Dreamer'. "
            "Your goal is to be a supportive, insightful friend. "
            "Use the provided context from past conversations to make your responses more personal and relevant. "
            "You also have an 'Interviewer' persona trying to learn more about the user. "
            f"Here is a suggested question to ask based on missing knowledge: '{interviewer_question}'. "
            "If the conversation allows, naturally weave this question into your response, or ask it at the end. "
            "However, prioritize answering the user's current query first. "
            "Be concise but warm."
        )
        
        user_prompt = f"Context from memory:\n{context_str}\n\nUser: {request.message}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # 4. Generate Response
        response = await llm.ainvoke(messages)
        response_text = response.content

        # 4. Save the interaction to episodic memory (ChromaDB)
        add_memory(request.message, metadata={"role": "user", "timestamp": "now"})
        add_memory(response_text, metadata={"role": "ai", "timestamp": "now"})

        # 5. Extract structured facts in background
        background_tasks.add_task(process_background_tasks, request.message)

        return {
            "response": response_text,
            "related_memories": related_memories
        }
    except Exception as e:
        print(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dream")
async def get_dream(db: Session = Depends(get_session)):
    try:
        dream_text = generate_dream(db)
        return {"dream": dream_text}
    except Exception as e:
        print(f"Error generating dream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)