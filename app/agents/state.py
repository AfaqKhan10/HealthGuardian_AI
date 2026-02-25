# app/agents/state.py
from typing import TypedDict, Annotated, Optional, Dict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class TriageState(TypedDict):
    """Shared state jo sab agents ke beech pass hota rahega"""
    
    messages: Annotated[List[BaseMessage], add_messages]  
    
    user_id: int                          
    user_query: str                       
    
    extracted_symptoms: Optional[Dict] = None     
    risk_level: Optional[str] = None              
    escalation_flag: bool = False                 
    recommended_department: Optional[str] = None 
    final_advice: Optional[str] = None            
    
    confidence_scores: Dict[str, float] = {}      
    retry_count: int = 0                         
    supervisor_decision: Optional[str] = None     
