from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from sqlmodel import Session, select
from models import Fact
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_gaps_and_ask(db: Session) -> str:
    """
    Analyzes known facts and generates a question to fill information gaps.
    """
    # 1. Fetch all known facts
    facts = db.exec(select(Fact)).all()
    known_info = "\n".join([f"- [{f.category}] {f.content}" for f in facts])
    
    if not known_info:
        known_info = "No facts known yet."

    # 2. Initialize Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

    # 3. Prompt to find gaps and ask
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the 'Interviewer' aspect of a personal AI companion.
Your goal is to learn more about the user to build a richer memory for future dreams and conversations.
Analyze the known facts below. Identify what is missing.
Look for gaps in:
- Basic demographics (Age, Location, Profession)
- Favorites (Colors, Foods, Seasons, Books, Music)
- Deep History (Childhood memories, Pivotal life moments)
- Current Context (Projects, stress levels, goals)

Select ONE missing piece of information that would be interesting to learn right now.
Generate a natural, conversational question to ask the user about it.
Do not be interrogative. Be curious and warm.
Only return the question."""),
        ("human", f"Known Facts:\n{known_info}\n\nGenerate one question to fill a gap.")
    ])

    chain = prompt | llm

    try:
        response = chain.invoke({})
        return response.content
    except Exception as e:
        print(f"Error in Interviewer: {e}")
        return "Tell me a small detail about your day?"