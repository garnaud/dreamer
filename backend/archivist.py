from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from sqlmodel import Session
from models import Fact
import os
from dotenv import load_dotenv

load_dotenv()

# Define the schema for structured output
class ExtractedFact(BaseModel):
    category: str = Field(description="The category of the fact (e.g., 'Personal', 'Work', 'Preference', 'Relationship', 'Goal')")
    content: str = Field(description="The concise fact extracted from the text (e.g. 'User lives in Paris').")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")

class FactList(BaseModel):
    facts: List[ExtractedFact]

def extract_and_save_facts(user_input: str, db: Session):
    """
    Extracts facts from user input and saves them to the SQLite database.
    """
    print(f"Archivist analyzing: {user_input}")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("Skipping fact extraction: No API Key")
        return

    # Initialize a dedicated LLM instance for extraction (low temperature for precision)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    # Configure structured output
    structured_llm = llm.with_structured_output(FactList)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert archivist. Your goal is to extract long-term facts about the user from their messages.
Ignore fleeting thoughts, questions, or small talk (e.g. 'Hello', 'How are you', 'What is the weather').
Focus on:
- Personal details (names, dates, location)
- Preferences (likes, dislikes)
- Relationships (friends, family)
- Work/Projects
- Goals/Dreams
If no relevant facts are found, return an empty list."""),
        ("human", "{input}")
    ])

    chain = prompt | structured_llm

    try:
        result = chain.invoke({"input": user_input})
        
        if result and result.facts:
            count = 0
            for extracted in result.facts:
                # Simple check to avoid duplicates could be added here (e.g. vector search or exact match)
                # For now, we just log it.
                print(f"Archivist found fact: [{extracted.category}] {extracted.content}")
                
                new_fact = Fact(
                    category=extracted.category,
                    content=extracted.content,
                    confidence_score=extracted.confidence
                )
                db.add(new_fact)
                count += 1
            
            if count > 0:
                db.commit()
                print(f"Archivist saved {count} new facts.")
        else:
            print("Archivist found no facts.")

    except Exception as e:
        print(f"Error in Archivist: {e}")
