# app/agents/workers/symptom_extractor.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import json

from app.config import settings
from app.agents.state import TriageState


# LLM setup (Groq)
llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",  # ya "mixtral-8x7b-32768" waghera jo pasand ho
    temperature=0.0,                        # structured output ke liye low temperature best
    max_tokens=600,
)


def load_prompt(filename: str) -> str:
    """Helper to read prompt from file"""
    path = f"app/prompts/{filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# Symptom extraction prompt load karo
SYMPTOM_PROMPT = load_prompt("symptom_extraction_prompt.txt")


def symptom_extractor_node(state: TriageState) -> TriageState:
    """
    Symptom Extractor worker agent.
    User query se structured symptoms nikaalta hai aur state update karta hai.
    Output JSON format mein deta hai.
    """
    user_query = state["user_query"]
    messages = state["messages"]

    # Prompt banao
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYMPTOM_PROMPT),
        ("human", "User query: {user_query}\n\nExtract symptoms as per instructions."),
    ])

    # Chain banao: prompt → LLM → JSON parser
    parser = JsonOutputParser()
    chain = prompt | llm | parser

    try:
        # LLM call karo
        extracted = chain.invoke({"user_query": user_query})

        # Validation (optional – agar LLM galat format de to fallback)
        if not isinstance(extracted, dict) or "symptoms" not in extracted:
            extracted = {
                "symptoms": [],
                "duration": "unknown",
                "severity": "unknown",
                "associated_factors": []
            }

    except OutputParserException:
        # Agar parsing fail ho jaye
        extracted = {
            "symptoms": [],
            "duration": "unknown",
            "severity": "unknown",
            "associated_factors": []
        }

    # State update karo
    updated_state = state.copy()
    updated_state["extracted_symptoms"] = extracted
    updated_state["messages"] = messages + [
        {"role": "assistant", "content": f"Symptom Extractor output: {json.dumps(extracted, ensure_ascii=False)}"}
    ]

    # Optional: confidence score supervisor ke liye add kar sakte ho (abhi simple)
    updated_state["confidence_scores"] = updated_state.get("confidence_scores", {})
    updated_state["confidence_scores"]["symptom_extractor"] = 0.85  # dummy – baad mein real logic se

    return updated_state


# Quick test (file ko direct run kar ke check kar sakte ho)
if __name__ == "__main__":
    test_state = TriageState(
        messages=[],
        user_query="Mujhe 3 din se tez sar dard hai, vomiting bhi ho rahi hai aur aankhen chamak rahi hain",
        user_id=1,
    )
    result = symptom_extractor_node(test_state)
    print("Extracted symptoms:")
    print(json.dumps(result["extracted_symptoms"], indent=2, ensure_ascii=False))