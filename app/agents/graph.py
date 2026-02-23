# app/agents/graph.py

from langgraph.graph import StateGraph, END
from typing import Literal
from app.agents.state import TriageState
from app.agents.supervisor import supervisor_node
from app.agents.workers.symptom_extractor import symptom_extractor_node
from app.agents.workers.risk_assessor import risk_assessor_node
from app.agents.workers.department_router import department_router_node
from app.agents.workers.advice_generator import advice_generator_node


workflow = StateGraph(state_schema=TriageState)

# Add nodes
workflow.add_node("symptom_extractor", symptom_extractor_node)
workflow.add_node("risk_assessor", risk_assessor_node)
workflow.add_node("department_router", department_router_node)
workflow.add_node("advice_generator", advice_generator_node)
workflow.add_node("supervisor", supervisor_node)

# Entry
workflow.set_entry_point("symptom_extractor")

# Linear flow via supervisor
workflow.add_edge("symptom_extractor", "supervisor")
workflow.add_edge("risk_assessor", "supervisor")
workflow.add_edge("department_router", "supervisor")
workflow.add_edge("advice_generator", "supervisor")


# ---------------- ROUTER ---------------- #

def supervisor_router(
    state: TriageState
) -> Literal["risk_assessor", "department_router", "advice_generator", "__end__"]:

    if state.get("escalation_flag"):
        return "__end__"

    # Step progression logic
    if not state.get("extracted_symptoms"):
        return "symptom_extractor"

    if not state.get("risk_level") or state.get("risk_level") == "UNKNOWN":
        return "risk_assessor"

    if not state.get("recommended_department"):
        return "department_router"

    if not state.get("final_advice"):
        return "advice_generator"

    return "__end__"


workflow.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "symptom_extractor": "symptom_extractor",
        "risk_assessor": "risk_assessor",
        "department_router": "department_router",
        "advice_generator": "advice_generator",
        "__end__": END,
    }
)

graph = workflow.compile()


# -------- TEST -------- #

if __name__ == "__main__":

    initial_state = TriageState(
        messages=[],
        user_query="Mujhe 3 din se tez sar dard hai, vomiting bhi ho rahi hai aur aankhen chamak rahi hain",
        user_id=1,
    )

    final_state = graph.invoke(initial_state)

    print("\nFinal state:")
    print("Risk level:", final_state.get("risk_level"))
    print("Department:", final_state.get("recommended_department"))
    print("Final advice:", final_state.get("final_advice"))
    print("Escalation:", final_state.get("escalation_flag"))
