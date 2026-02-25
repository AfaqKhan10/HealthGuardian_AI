# app/agents/workers/advice_generator.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

from app.config import settings
from app.agents.state import TriageState


llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.2,  
    max_tokens=500,
)


def load_prompt(filename: str) -> str:
    path = f"app/prompts/{filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


ADVICE_PROMPT = load_prompt("advice_prompt.txt")


def advice_generator_node(state: TriageState) -> TriageState:
    symptoms = state.get("extracted_symptoms", {})
    risk_level = state.get("risk_level", "UNKNOWN")
    department = state.get("recommended_department", "General Physician")
    messages = state["messages"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", ADVICE_PROMPT),
        ("human", "Symptoms: {symptoms_json}\nRisk level: {risk_level}\nRecommended department: {department}\nGenerate safe advice."),
    ])

    chain = prompt | llm | JsonOutputParser()

    try:
        result = chain.invoke({
            "symptoms_json": json.dumps(symptoms, ensure_ascii=False),
            "risk_level": risk_level,
            "department": department
        })
        print("Parsed advice result:", result)  # debug

        advice_text = result.get("advice_text", "Consult a doctor soon.")
        disclaimer = result.get("disclaimer", "This is general guidance only. Consult a qualified doctor or emergency services (1122) immediately if symptoms worsen.")
        confidence = result.get("confidence", 0.5)

    except Exception as e:
        print("Advice parsing error:", str(e))
        advice_text = "Please see a doctor as soon as possible."
        disclaimer = "This is general guidance only. Consult a qualified doctor or emergency services (1122) immediately if symptoms worsen."
        confidence = 0.0

    updated_state = state.copy()
    updated_state["final_advice"] = f"{advice_text}\n\n{disclaimer}"
    updated_state["confidence_scores"] = updated_state.get("confidence_scores", {})
    updated_state["confidence_scores"]["advice_generator"] = confidence
    updated_state["messages"] = messages + [
        {"role": "assistant", "content": f"Advice Generator: {advice_text}"}
    ]

    return updated_state


# Test
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
        risk_level="HIGH",
        recommended_department="Neurology"
    )
    result = advice_generator_node(test_state)
    print("\nFinal advice:", result["final_advice"])
    print("Confidence:", result["confidence_scores"].get("advice_generator"))
