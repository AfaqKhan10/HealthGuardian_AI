# app/agents/workers/department_router.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

from app.config import settings
from app.agents.state import TriageState


llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.0,
    max_tokens=300,
)


def load_prompt(filename: str) -> str:
    path = f"app/prompts/{filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


ROUTING_PROMPT = load_prompt("routing_prompt.txt")


def department_router_node(state: TriageState) -> TriageState:
    symptoms = state.get("extracted_symptoms", {})
    risk_level = state.get("risk_level", "UNKNOWN")
    messages = state["messages"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTING_PROMPT),
        ("human", "Extracted symptoms: {symptoms_json}\nRisk level: {risk_level}\nSuggest department."),
    ])

    chain = prompt | llm | JsonOutputParser()

    try:
        result = chain.invoke({
            "symptoms_json": json.dumps(symptoms, ensure_ascii=False),
            "risk_level": risk_level
        })
        print("Parsed routing result:", result)  # debug
        department = result.get("recommended_department", "General Physician")
        reason = result.get("reason", "No reason")
        confidence = result.get("confidence", 0.5)
    except Exception as e:
        print("Routing parsing error:", str(e))
        department = "General Physician"
        reason = "Routing failed - " + str(e)
        confidence = 0.0

    updated_state = state.copy()
    updated_state["recommended_department"] = department
    updated_state["confidence_scores"] = updated_state.get("confidence_scores", {})
    updated_state["confidence_scores"]["department_router"] = confidence
    updated_state["messages"] = messages + [
        {"role": "assistant", "content": f"Department Router: {department} - {reason}"}
    ]

    return updated_state


if __name__ == "__main__":
    test_state = TriageState(
        messages=[],
        user_query="Mujhe 3 din se tez sar dard hai, vomiting bhi ho rahi hai aur aankhen chamak rahi hain",
        user_id=1,
        extracted_symptoms={
            "symptoms": ["headache", "vomiting", "blurred vision"],
            "duration": "3 days",
            "severity": "severe"
        },
        risk_level="HIGH"
    )
    result = department_router_node(test_state)
    print("Recommended department:", result["recommended_department"])
    print("Reason:", result.get("messages")[-1]["content"])