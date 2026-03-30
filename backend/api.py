from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import re

# Import LangChain message types
from langchain_core.messages import HumanMessage, AIMessage

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.graph import get_compiled_agent

# Initialize FastAPI app
app = FastAPI(
    title="CyberFirstAid AI API",
    description="API for Mobile App to interact with the CyberFirstAid AI ReAct Agent.",
    version="1.0.0"
)

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MODELS ──────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en" # "en" or "sw"

class MessageItem(BaseModel):
    role: str
    content: str
    
class AgentStateData(BaseModel):
    current_stage: str
    helplessness_score: Optional[int] = None
    wants_report: Optional[bool] = None
    incident_category: Optional[str] = None
    incident_severity: Optional[str] = None
    classification_reasoning: Optional[str] = None
    recommended_channels: Optional[List[str]] = None
    chosen_channel: Optional[str] = None
    technical_steps: Optional[List[str]] = None
    technical_summary: Optional[str] = None
    tzcert_fields: Optional[Dict[str, Any]] = None
    report_template: Optional[str] = None
    submission_instructions: Optional[str] = None
    emotional_response: Optional[str] = None
    resilience_exercise: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]
    state: AgentStateData

# ── IN-MEMORY STORAGE ───────────────────────────────
# In a production app, use Redis or a database to persist this state.
SESSIONS: Dict[str, Any] = {}

# ── UTILS ───────────────────────────────────────────

def clean_ai_content(content: str) -> str:
    if not content:
        return ""
    # Remove Groq's raw XML-style tool call leakage
    cleaned = re.sub(r"<function=.*?>.*?</function>", "", content, flags=re.DOTALL)
    cleaned = re.sub(r"<tool_call>.*?</tool_call>", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()

def init_agent_state(lang: str) -> dict:
    welcome_msg = (
        "Hello. I am CyberFirstAid AI. How can I help you today? Do you need to report a cyber incident?" 
        if lang == "en" else 
        "Hujambo. Mimi ni msaidizi wa CyberFirstAid AI. Nikusaidie nini leo? Je, unahitaji kuripoti tukio la kimtandao?"
    )
    return {
        "messages": [AIMessage(content=welcome_msg)],
        "language": lang,
        "current_stage": "1_classification",
        "helplessness_score": None,
        "wants_report": None,
        "incident_category": None,
        "incident_severity": None,
        "classification_reasoning": None,
        "recommended_channels": None,
        "chosen_channel": None,
        "technical_steps": None,
        "technical_summary": None,
        "tzcert_fields": None,
        "report_template": None,
        "submission_instructions": None,
        "emotional_response": None,
        "resilience_exercise": None,
        "confidence_before": None,
        "confidence_after": None,
        "error": None
    }

# ── ENDPOINTS ───────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    x_groq_api_key: Optional[str] = Header(None, alias="X-Groq-API-Key")
):
    """
    Main endpoint for the mobile app to communicate with the Agent.
    Requires a session_id to maintain dialogue history.
    API key can be passed via X-Groq-API-Key header or set as environment variable.
    """
    # Use header API key if provided, otherwise fall back to environment variable
    api_key = x_groq_api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API Key is required. Set X-Groq-API-Key header or GROQ_API_KEY environment variable.")
    
    # Set the API key for this request
    os.environ["GROQ_API_KEY"] = api_key

    session_id = request.session_id
    
    # Initialize session if new
    if session_id not in SESSIONS:
        SESSIONS[session_id] = init_agent_state(request.language)
        
    # Get current state and update
    state = SESSIONS[session_id]
    state["language"] = request.language
    
    # Append the user's new message
    state["messages"].append(HumanMessage(content=request.message))
    
    previous_msg_count = len(state["messages"])
    
    try:
        # Invoke agent
        agent = get_compiled_agent()
        new_state = agent.invoke(state)
        
        # Save updated state
        SESSIONS[session_id] = new_state
        
        # Extract new AI messages generated in this turn
        new_messages = []
        for msg in new_state["messages"][previous_msg_count:]:
            if isinstance(msg, AIMessage):
                cleaned_text = clean_ai_content(msg.content)
                if cleaned_text:
                    new_messages.append(MessageItem(role="assistant", content=cleaned_text))
                    
        # If no explicit AI text was output (e.g. only tool execution), we can send an empty list
        
        # Build dashboard state response
        state_data = AgentStateData(
            current_stage=new_state.get("current_stage", "1_classification"),
            helplessness_score=new_state.get("helplessness_score"),
            wants_report=new_state.get("wants_report"),
            incident_category=new_state.get("incident_category"),
            incident_severity=new_state.get("incident_severity"),
            classification_reasoning=new_state.get("classification_reasoning"),
            recommended_channels=new_state.get("recommended_channels"),
            chosen_channel=new_state.get("chosen_channel"),
            technical_steps=new_state.get("technical_steps"),
            technical_summary=new_state.get("technical_summary"),
            tzcert_fields=new_state.get("tzcert_fields"),
            report_template=new_state.get("report_template"),
            submission_instructions=new_state.get("submission_instructions"),
            emotional_response=new_state.get("emotional_response"),
            resilience_exercise=new_state.get("resilience_exercise"),
        )
        
        return ChatResponse(
            session_id=session_id,
            messages=new_messages,
            state=state_data
        )
        
    except Exception as e:
        # Revert the human message if it failed so they can retry safely
        state["messages"].pop()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}", response_model=ChatResponse)
async def get_session(session_id: str):
    """
    Optional: Endpoint to retrieve the entire current session context and history.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSIONS[session_id]
    
    all_messages = []
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            all_messages.append(MessageItem(role="user", content=msg.content))
        elif isinstance(msg, AIMessage):
            cleaned = clean_ai_content(msg.content)
            if cleaned:
                all_messages.append(MessageItem(role="assistant", content=cleaned))
                
    state_data = AgentStateData(
        current_stage=state.get("current_stage", "1_classification"),
        helplessness_score=state.get("helplessness_score"),
        wants_report=state.get("wants_report"),
        incident_category=state.get("incident_category"),
        incident_severity=state.get("incident_severity"),
        classification_reasoning=state.get("classification_reasoning"),
        recommended_channels=state.get("recommended_channels"),
        chosen_channel=state.get("chosen_channel"),
        technical_steps=state.get("technical_steps"),
        technical_summary=state.get("technical_summary"),
        tzcert_fields=state.get("tzcert_fields"),
        report_template=state.get("report_template"),
        submission_instructions=state.get("submission_instructions"),
        emotional_response=state.get("emotional_response"),
        resilience_exercise=state.get("resilience_exercise"),
    )
    
    return ChatResponse(
        session_id=session_id,
        messages=all_messages,
        state=state_data
    )

if __name__ == "__main__":
    import uvicorn
    # Make sure to run with your GROQ_API_KEY environment variable set
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
