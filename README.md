# HealthGuardian AI

**HealthGuardian AI** is a multi-agent AI-powered medical triage system built with FastAPI and LangGraph. It takes user symptoms in natural language (Urdu or English), analyzes them using specialized agents, assesses risk level, suggests appropriate medical department, and provides **safe, non-diagnostic guidance** with clear disclaimers.

**Important**: This is NOT a medical diagnosis tool. It only helps triage symptoms and guide users to seek proper medical help.

## Features

- Multi-agent architecture using **LangGraph**:
  - Symptom Extractor Agent
  - Risk Assessor Agent
  - Department Router Agent
  - Advice Generator Agent
  - Supervisor Agent (orchestrates, validates, retries, escalates)
- LLM powered by **Groq** (Llama 3.3 70B Versatile)
- FastAPI backend with Swagger UI for testing
- PostgreSQL database for storing triage cases
- Graceful handling of irrelevant/non-medical queries
- Clear escalation for critical symptoms (e.g., chest pain + shortness of breath → "Call 1122 immediately")

## Tech Stack

- Backend: FastAPI
- Agent Framework: LangGraph + LangChain
- LLM: Groq (llama-3.3-70b-versatile)
- Database: PostgreSQL (SQLAlchemy)
- Authentication: Planned (JWT in future)
- Deployment Ready: Docker support coming soon

## Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL installed & running
- Groq API key[](https://console.groq.com)

### Step 1: Clone the repo
```bash
git clone https://github.com/YourUsername/HealthGuardian_AI.git
cd HealthGuardian_AI
