# app/agents/workers/risk_assessor.py

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

from app.config import settings
from app.agents.state import TriageState


# ------------------ LLM Setup ------------------

llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.0,
    max_tokens=400,
)


def load_prompt(filename: str) -> str:
    path = f"app/prompts/{filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


RISK_PROMPT = load_prompt("risk_assessment_prompt.txt")


# ------------------ Risk Assessor Node ------------------

def risk_assessor_node(state: TriageState) -> TriageState:
    symptoms = state.get("extracted_symptoms", {})
    messages = state.get("messages", [])

    prompt = ChatPromptTemplate.from_messages([
        ("system", RISK_PROMPT),
    ])

    chain = prompt | llm | JsonOutputParser()

    try:
        result = chain.invoke({
            "extracted_symptoms": json.dumps(symptoms, ensure_ascii=False)
        })

        print("Full LLM Result:", result)  # debug (remove in production)

        risk_level = result.get("risk_level", "UNKNOWN")
        reason = result.get("reason") or "Model did not provide reason"
        confidence = result.get("confidence", 0.0)

    except Exception as e:
        print("Parsing error:", str(e))
        risk_level = "UNKNOWN"
        reason = "Assessment failed: " + str(e)
        confidence = 0.0

    updated_state = state.copy()
    updated_state["risk_level"] = risk_level

    updated_state["confidence_scores"] = updated_state.get("confidence_scores", {})
    updated_state["confidence_scores"]["risk_assessor"] = confidence

    updated_state["messages"] = messages + [
        {
            "role": "assistant",
            "content": f"Risk Assessor: {risk_level} - {reason}"
        }
    ]

    return updated_state


# ------------------ Test ------------------

if __name__ == "__main__":
    test_state = TriageState(
        messages=[],
        user_query="Mujhe 3 din se tez sar dard hai, vomiting bhi ho rahi hai aur aankhen chamak rahi hain",
        user_id=1,
        extracted_symptoms={
            "symptoms": ["headache", "vomiting", "blurred vision"],
            "duration": "3 days",
            "severity": "severe"
        }
    )

    result = risk_assessor_node(test_state)

    print("\nRisk level:", result["risk_level"])
    print("Reason:", result.get("messages")[-1]["content"])
