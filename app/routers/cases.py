# app/routers/cases.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PatientCaseCreate
from app.models import PatientCase
from app.agents.graph import graph
from app.agents.state import TriageState

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/", response_model=dict)
def create_patient_case(
    case_in: PatientCaseCreate,
    db: Session = Depends(get_db)
):
    # Initial state for graph
    initial_state = TriageState(
        messages=[],
        user_query=case_in.user_query,
        user_id=None,  # No user_id needed for now
    )

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage failed: {str(e)}")

    # Create DB entry (user_id skipped/NULL)
    db_case = PatientCase(
        user_id=0,
        user_query=case_in.user_query,
        extracted_symptoms=final_state.get("extracted_symptoms"),
        risk_level=final_state.get("risk_level"),
        escalation_flag=final_state.get("escalation_flag", False),
        status="completed" if not final_state.get("escalation_flag") else "escalated",
        final_response=final_state.get("final_advice"),
    )

    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    # Return full result
    return {
        "id": db_case.id,
        "query": case_in.user_query,
        "extracted_symptoms": db_case.extracted_symptoms,
        "risk_level": db_case.risk_level,
        "department": final_state.get("recommended_department"),
        "advice": db_case.final_response,
        "escalation_flag": db_case.escalation_flag,
        "status": db_case.status
    }