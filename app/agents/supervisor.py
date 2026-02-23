# app/agents/supervisor.py

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any
import json

from app.config import settings
from app.agents.state import TriageState


llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=800,
)


def load_prompt(filename: str) -> str:
    path = f"app/prompts/{filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


SUPERVISOR_PROMPT = load_prompt("supervisor_prompt.txt")


def supervisor_node(state: TriageState) -> Dict[str, Any]:

    messages = state.get("messages", [])
    extracted_symptoms = state.get("extracted_symptoms", {})
    risk_level = state.get("risk_level")
    retry_count = state.get("retry_count", 0)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=f"""
Current state:
User query: {state.get('user_query')}
Extracted symptoms: {json.dumps(extracted_symptoms, ensure_ascii=False)}
Risk level: {risk_level}
Retry count: {retry_count}

Decide next step.
Return ONLY valid JSON.
        """)
    ])

    chain = prompt | llm
    response = chain.invoke({})

    try:
        supervisor_output = json.loads(response.content.strip())
    except Exception:
        supervisor_output = {
            "supervisor_decision": "approved",
            "reason": "Fallback safe decision",
            "final_escalation_flag": False,
            "confidence_scores": {}
        }

    new_state = state.copy()

    new_state["supervisor_decision"] = supervisor_output.get("supervisor_decision", "approved")
    new_state["reason"] = supervisor_output.get("reason", "")
    new_state["escalation_flag"] = supervisor_output.get("final_escalation_flag", False)
    new_state["confidence_scores"] = supervisor_output.get("confidence_scores", {})

    if supervisor_output.get("supervisor_decision") == "retry":
        new_state["retry_count"] = retry_count + 1
    else:
        new_state["retry_count"] = retry_count

    new_state["messages"] = messages + [
        {"role": "assistant", "content": f"Supervisor: {new_state['supervisor_decision']}"}
    ]

    # Emergency override
    if new_state["escalation_flag"]:
        new_state["final_advice"] = "EMERGENCY: Call 1122 immediately!"
        new_state["status"] = "escalated"

    return new_state