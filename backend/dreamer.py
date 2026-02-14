from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from sqlmodel import Session, select
from models import Fact
from vector_store import search_memories
import os
from dotenv import load_dotenv

load_dotenv()

def generate_dream(db: Session):
    """
    Retrieves facts and memories to synthesize a poetic dream sequence.
    """
    # 1. Fetch some random facts to spark inspiration
    statement = select(Fact).order_by(Fact.id.desc()).limit(10)
    facts = db.exec(statement).all()
    facts_str = "\n".join([f"- {f.category}: {f.content}" for f in facts])

    # 2. Fetch some recent episodic memories
    memories = search_memories("feelings and events", n_results=5)
    memories_str = ""
    if memories and memories['documents']:
        memories_str = "\n".join([f"- {doc}" for doc in memories['documents'][0]])

    # 3. Initialize Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.8)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are 'The Dreamer'. Your role is to take the fragments of the user's life (facts and memories) 
and weave them into a poetic, metaphorical dream sequence. 
Do not just summarize; transform reality into symbols and echoes.
Be ethereal, supportive, and slightly mysterious. 
The goal is to help the user see their life from a beautiful, new perspective.
Use rich imagery."""),
        ("human", f"""Fragmented facts:
{facts_str}

Recent echoes of memory:
{memories_str}

Weave me a dream.""")
    ])

    chain = prompt | llm

    try:
        print("Dreamer is weaving a new dream...")
        result = chain.invoke({})
        return result.content
    except Exception as e:
        print(f"Error in Dreamer: {e}")
        return "The dream faded before it could be spoken..."
