# app/agents/state.py
from typing import TypedDict, Annotated, Optional, Dict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class TriageState(TypedDict):
    """Shared state jo sab agents ke beech pass hota rahega"""
    
    messages: Annotated[List[BaseMessage], add_messages]  # chat history / messages jo LLM ko jaate hain
    
    user_id: int                          # kis user ka case hai (JWT se aayega baad mein)
    user_query: str                       # raw user input (symptoms ki baat)
    
    extracted_symptoms: Optional[Dict] = None     # symptom_extractor se aayega, e.g. {"symptoms": ["headache", "fever"]}
    risk_level: Optional[str] = None              # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    escalation_flag: bool = False                 # life-threatening case to true
    recommended_department: Optional[str] = None  # "Emergency", "Cardiology", etc.
    final_advice: Optional[str] = None            # safe advice jo user ko dikhega
    
    confidence_scores: Dict[str, float] = {}      # har agent ka score, e.g. {"symptom_extractor": 0.92}
    retry_count: int = 0                          # current retry count (supervisor ke liye)
    supervisor_decision: Optional[str] = None     # "approved", "retry", "override", "escalated"