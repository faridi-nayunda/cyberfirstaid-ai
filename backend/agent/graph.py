"""
CyberFirstAid AI - LangGraph ReAct Agent
Implements a strict conversational ReAct agent with 4 stages 
and custom tools that update the global state.
"""

import json
import os
from typing import Annotated, TypedDict, Optional, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool

# ─────────────────────────────────────────────
# CONFIG & CONSTANTS
# ─────────────────────────────────────────────
TZCERT_FIELD_MAP = {
    "full_device_compromise": {
        "type": "Incident",
        "subject": "Intrusions",
        "category": "Compromise unprivileged account",
        "subject_note_en": "Select 'Intrusions' — an attacker gained full control of your device.",
        "subject_note_sw": "Chagua 'Intrusions' — mshambuliaji alipata udhibiti kamili wa kifaa chako.",
        "category_note_en": "Select 'Compromise unprivileged account' — your device/account was fully taken over.",
        "category_note_sw": "Chagua 'Compromise unprivileged account' — kifaa/akaunti yako ilichukuliwa kabisa.",
    },
    "airtel_money_scam": {
        "type": "Incident",
        "subject": "Fraud",
        "category": "Phishing",
        "subject_note_en": "Select 'Fraud' — you were financially deceived via mobile money.",
        "subject_note_sw": "Chagua 'Fraud' — ulidanganywa kifedha kupitia pesa za simu.",
        "category_note_en": "Select 'Phishing' — the attacker impersonated someone to trick you.",
        "category_note_sw": "Chagua 'Phishing' — mshambuliaji aliiga mtu ili akudangaye.",
    },
    "mpesa_scam": {
        "type": "Incident",
        "subject": "Fraud",
        "category": "Phishing",
        "subject_note_en": "Select 'Fraud' — you were financially deceived via mobile money.",
        "subject_note_sw": "Chagua 'Fraud' — ulidanganywa kifedha kupitia pesa za simu.",
        "category_note_en": "Select 'Phishing' — the attacker impersonated someone to trick you.",
        "category_note_sw": "Chagua 'Phishing' — mshambuliaji aliiga mtu ili akudangaye.",
    },
    "tigo_pesa_scam": {
        "type": "Incident",
        "subject": "Fraud",
        "category": "Phishing",
        "subject_note_en": "Select 'Fraud' — you were financially deceived via mobile money.",
        "subject_note_sw": "Chagua 'Fraud' — ulidanganywa kifedha kupitia pesa za simu.",
        "category_note_en": "Select 'Phishing' — the attacker impersonated someone to trick you.",
        "category_note_sw": "Chagua 'Phishing' — mshambuliaji aliiga mtu ili akudangaye.",
    },
    "account_takeover": {
        "type": "Incident",
        "subject": "Intrusions",
        "category": "Compromise unprivileged account",
        "subject_note_en": "Select 'Intrusions' — someone broke into and took over your account.",
        "subject_note_sw": "Chagua 'Intrusions' — mtu aliingia na kuchukua akaunti yako.",
        "category_note_en": "Select 'Compromise unprivileged account' — your social media/email account was compromised.",
        "category_note_sw": "Chagua 'Compromise unprivileged account' — akaunti yako ya mitandao ya kijamii/barua pepe iliathirika.",
    },
    "malware_infection": {
        "type": "Incident",
        "subject": "Malicious Code",
        "category": "Trojan",
        "subject_note_en": "Select 'Malicious Code' — harmful software was installed on your device.",
        "subject_note_sw": "Chagua 'Malicious Code' — programu hasidi ilisakinishwa kwenye kifaa chako.",
        "category_note_en": "Select 'Trojan' for RAT/spyware/hidden malware. If ransomware locked your files, select 'Ransomware'.",
        "category_note_sw": "Chagua 'Trojan' kwa RAT/spyware. Kama ransomware ilifunga faili zako, chagua 'Ransomware'.",
    },
    "data_breach": {
        "type": "Incident",
        "subject": "Information Security",
        "category": "Unauthorized access to information",
        "subject_note_en": "Select 'Information Security' — your personal data was exposed or accessed.",
        "subject_note_sw": "Chagua 'Information Security' — data yako binafsi ilifichuliwa au kufikiwa.",
        "category_note_en": "Select 'Unauthorized access to information' — someone accessed your data without permission.",
        "category_note_sw": "Chagua 'Unauthorized access to information' — mtu alifikia data yako bila ruhusa.",
    },
    "unknown": {
        "type": "Incident",
        "subject": "Others",
        "category": "All Incidents that do not fit in one of the above categories",
        "subject_note_en": "Select 'Others' — your incident does not clearly fit the other categories.",
        "subject_note_sw": "Chagua 'Others' — tukio lako halifiti wazi kwenye kategoria nyingine.",
        "category_note_en": "Select 'All Incidents that do not fit in one of the above categories'.",
        "category_note_sw": "Chagua 'All Incidents that do not fit in one of the above categories'.",
    },
}

# ─────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    language: str
    current_stage: str
    
    # UI Dashboard elements (populated by tools)
    helplessness_score: Optional[int]
    wants_report: Optional[bool]
    incident_category: Optional[str]
    incident_severity: Optional[str]
    classification_reasoning: Optional[str]
    recommended_channels: Optional[List[str]]
    chosen_channel: Optional[str]
    technical_steps: Optional[List[str]]
    technical_summary: Optional[str]
    tzcert_fields: Optional[dict]
    report_template: Optional[str]
    submission_instructions: Optional[str]
    emotional_response: Optional[str]
    resilience_exercise: Optional[str]
    confidence_before: Optional[int]
    confidence_after: Optional[int]
    error: Optional[str]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def load_playbooks() -> dict:
    data_path = os.path.join(os.path.dirname(__file__), "../data/playbooks.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        temperature=0.2, # Low temp for reliable tool calling
        max_tokens=2048,
    )

# ─────────────────────────────────────────────
# AGENT TOOLS (DUMMY DECLARATIONS FOR LLM BINDING)
# ─────────────────────────────────────────────
@tool
def classify_incident(category: str, severity: str, reasoning: str):
    """Classifies the cyber incident to determine the correct technical playbook.
    category MUST be one of: full_device_compromise, airtel_money_scam, mpesa_scam, tigo_pesa_scam, account_takeover, malware_infection, data_breach, unknown.
    severity MUST be one of: low, medium, high, critical.
    reasoning: A brief 1-sentence explanation.
    """
    pass

@tool
def get_technical_playbook(category: str):
    """Retrieves the official technical recovery and mitigation steps for the given incident category.
    Use this immediately after classifying the incident so the user gets actionable advice.
    """
    pass

@tool
def generate_report_template(user_summary: str, category: str):
    """Generates an official formal incident report template for TZ-CERT based on the user's situation.
    Call this ONLY IF the user explicitly replies 'Yes' to wanting a report.
    """
    pass

@tool
def emotional_checkin(category: str, score: int):
    """Provides a tailored trauma-informed emotional check-in and resilience exercise for the user.
    score: An integer from 1 to 10 based on the user's answer to the helplessness scale.
    Call this ONLY AFTER the user provides their 1-10 helplessness/scared score. 
    """
    pass

tools = [classify_incident, get_technical_playbook, generate_report_template, emotional_checkin]

# ─────────────────────────────────────────────
# TOOL EXECUTION LOGIC
# ─────────────────────────────────────────────
def run_classify_incident(category: str, severity: str, reasoning: str) -> tuple[str, dict]:
    playbooks = load_playbooks()
    matched = next((i for i in playbooks["incident_types"] if i["id"] == category), None)
    
    if matched:
        channels = matched["reporting_channels"]
    else:
        channels = ["tzcert", "police"]
        
    updates = {
        "incident_category": category,
        "incident_severity": severity,
        "classification_reasoning": reasoning,
        "recommended_channels": channels,
        "chosen_channel": channels[0] if channels else "tzcert"
    }
    result_str = f"Successfully classified as {category} ({severity}). Recommended channels: {', '.join(channels)}. UI updated."
    return result_str, updates

def run_get_technical_playbook(category: str, language: str) -> tuple[str, dict]:
    playbooks = load_playbooks()
    matched = next((i for i in playbooks["incident_types"] if i["id"] == category), None)
    
    if matched:
        steps_key = "technical_steps_sw" if language == "sw" else "technical_steps_en"
        steps = matched.get(steps_key, matched.get("technical_steps_en", []))
        n = len(steps)
        summary = (
            f"Hapa kuna hatua {n} muhimu za kukusaidia kulinda akaunti na vifaa vyako mara moja:"
            if language == "sw" else
            f"Here are {n} critical steps to help you secure your accounts and devices immediately:"
        )
    else:
        steps = (
            ["Tafadhali nipe maelezo zaidi kuhusu kilichotokea."] if language == "sw"
            else ["Please describe what happened in more detail so I can provide accurate help."]
        )
        summary = (
            "Sikuelewa vizuri. Nipe maelezo zaidi ili nikusaidie ipasavyo." if language == "sw"
            else "I need more details to provide the correct steps."
        )
        
    updates = {
        "technical_steps": steps,
        "technical_summary": summary
    }
    result_str = f"Retrieved {len(steps)} technical steps. UI updated."
    return result_str, updates

def run_generate_report_template(user_summary: str, category: str, language: str) -> tuple[str, dict]:
    playbooks = load_playbooks()
    tzcert_map = TZCERT_FIELD_MAP.get(category, TZCERT_FIELD_MAP["unknown"])
    
    if language == "sw":
        message_body = f"Ninaandika kuripoti tukio la '{category}' ambalo nililipitia. {user_summary}. Naomba TZ-CERT inisaidie kuchunguza na kunipa mwongozo katika jambo hili."
        template = f"""╔══════════════════════════════════════════════════════════════╗
║         FOMU YA TZ-CERT — THAMANI ZA KUJAZA                ║
╚══════════════════════════════════════════════════════════════╝

Tumia maadili haya kujaza fomu kwenye tzcert.go.tz:

 AINA      →  ✅ {tzcert_map['type']}
 MADA      →  ✅ {tzcert_map['subject']}
 KATEGORIA →  ✅ {tzcert_map['category']}

──────────────────────────────────────────────────────────────
 UJUMBE — Nakili kila kitu kati ya mistari miwili hapa chini
──────────────────────────────────────────────────────────────
{message_body}
──────────────────────────────────────────────────────────────
💾 Hifadhi nambari ya kumbukumbu utakayopokea baada ya kutuma."""
        
        instructions = f"""### 📤 Jinsi ya Kutuma Ripoti (Hatua kwa Hatua)

1. **Fungua** 👉 [https://www.tzcert.go.tz/incident/report](https://www.tzcert.go.tz/incident/report)
2. **AINA** — Chagua **"{tzcert_map['type']}"**
3. **MADA** — Chagua **"{tzcert_map['subject']}"**
4. **KATEGORIA** — Chagua **"{tzcert_map['category']}"**
5. **UJUMBE** — Nakili ujumbe kutoka kwenye kisanduku hapo juu na ubandike.
6. Bonyeza **SUBMIT** 🟢"""

    else:
        message_body = f"I am writing to report a '{category}' incident that I experienced. {user_summary}. I kindly request TZ-CERT's assistance in investigating and resolving this matter."
        template = f"""╔══════════════════════════════════════════════════════════════╗
║         TZ-CERT FORM — VALUES TO FILL IN                   ║
╚══════════════════════════════════════════════════════════════╝

Use these values when filling the form on tzcert.go.tz:

 TYPE      →  ✅ {tzcert_map['type']}
 SUBJECT   →  ✅ {tzcert_map['subject']}
 CATEGORY  →  ✅ {tzcert_map['category']}

──────────────────────────────────────────────────────────────
 MESSAGE — Copy everything between the two lines below
──────────────────────────────────────────────────────────────
{message_body}
──────────────────────────────────────────────────────────────
💾 Save the reference number you receive after submitting."""
        
        instructions = f"""### 📤 How to Submit (Step by Step)

1. **Open** 👉 [https://www.tzcert.go.tz/incident/report](https://www.tzcert.go.tz/incident/report)
2. **TYPE** — Select **"{tzcert_map['type']}"**
3. **SUBJECT** — Select **"{tzcert_map['subject']}"**
4. **CATEGORY** — Select **"{tzcert_map['category']}"**
5. **MESSAGE** — Copy the message from the box above and paste it.
6. Click **SUBMIT** 🟢"""

    updates = {
        "tzcert_fields": tzcert_map,
        "report_template": template,
        "submission_instructions": instructions,
        "wants_report": True
    }
    return "Report template and submission instructions generated successfully. UI updated.", updates

def run_emotional_checkin(category: str, score: int, language: str) -> tuple[str, dict]:
    playbooks = load_playbooks()
    matched_note = ""
    for inc in playbooks["incident_types"]:
        if inc["id"] == category:
            key = "emotional_note_sw" if language == "sw" else "emotional_note_en"
            matched_note = inc.get(key, "")
            break

    if language == "sw":
        if score <= 3:
            ex = "✨ **Taarifa ya Nguvu:** Sema hivi kwa sauti: *'Nilichukua hatua leo. Ninadhibiti tena maisha yangu ya kidijitali.'*"
        elif score <= 6:
            ex = "🌿 **Zoezi la Ardhi:** Taja vitu **3** unavyoviona, **2** unavyovigusa, **1** unaloisikia. Hii inakurejesha kwenye wakati huu huu."
        else:
            ex = "🌬️ **Pumziko la Kutuliza:** Vuta pumzi kwa sekunde **4**... Shikilia **4**... Toa pumzi kwa **6**. Fanya mara **3**."
            
        comfort = f"{matched_note} Ujasiri wako ni mkubwa. Piga hatua moja kwa wakati."
    else:
        if score <= 3:
            ex = "✨ **Agency Statement:** Say out loud: *'I took action today. I am reclaiming control of my digital life.'*"
        elif score <= 6:
            ex = "🌿 **Grounding:** Name **3** things you see, **2** you can touch, **1** you hear. This brings you back to the present."
        else:
            ex = "🌬️ **Calming Breath:** Inhale **4** sec... Hold **4**... Exhale **6**. Repeat **3** times."
            
        comfort = f"{matched_note} Your courage is immense. Take things one step at a time."

    updates = {
        "emotional_response": comfort,
        "resilience_exercise": ex,
        "helplessness_score": score,
        "current_stage": "5_completed"
    }
    return f"Emotional comfort provided for score {score}. UI updated.", updates


# ─────────────────────────────────────────────
# LANGGRAPH NODES
# ─────────────────────────────────────────────
def agent_node(state: AgentState):
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)
    
    sys_msg_text = """You are CyberFirstAid AI, a warm, trauma-informed digital first responder for Tanzania citizens.
Your job is to support victims of cyber attacks through a STRICT multi-turn conversational flow.
You MUST progress through these 7 stages exactly in order. DO NOT skip stages or combine them. Never advance until the user has explicitly provided the required info or confirmation!

STAGE 1: Intent Check & Empathy
- Determine if the user is describing a cyber incident, OR just asking for a language switch, greeting, or casual talk.
- If it is NOT an incident description (e.g. "unaweza kutumia kiswahili?", "hello"):
    - Respond naturally and politely, switch languages if requested.
    - Ask gently: "How can I help you today? Do you want to report a cyber incident?"
    - STOP. Wait for the user. Do not proceed to Stage 2.
- If it IS an incident description, proceed to STAGE 2.

STAGE 2: Detailed Information Gathering
- Check if you have enough information to accurately classify the incident (e.g., if they say "I got scammed", ask "Which mobile money provider was it: M-Pesa, Airtel Money, or Tigo Pesa?").
- Ask 1-2 short clarifying questions if vital details are missing.
- If details are missing, STOP. Wait for the user to reply.
- If details are sufficient to map to a specific incident playbook, proceed to STAGE 3.

STAGE 3: Classify 
- Call `classify_incident` assigning it the most specific category possible (like `airtel_money_scam` instead of generic `mobile_money_scam`). 
- Briefly explain the classification to the user.
- IMMEDIATELY proceed to STAGE 4.

STAGE 4: Safety Protocols (Device Compromise)
- CRITICAL: If the device is classified as `full_device_compromise`, before offering ANY steps, explicitly instruct the user to disconnect from the internet/power off! Wait for confirmation to proceed.
- If they are not fully compromised, you can proceed to STAGE 5 in the same turn.

STAGE 5: Highly Personalized Technical Recovery
- Call `get_technical_playbook`.
- IMPORTANT: Present the technical steps clearly to the user. If the JSON didn't have an exact match for their bank or provider, gracefully adapt the closest playbook steps using your own intelligence (e.g., substitute "Airtel" with "NMB Bank" and advise them to call bank support).
- Ask the user if they were able to follow the steps and if they are safe.
- STOP. Wait for the user to confirm they are safe or ask further technical questions.

STAGE 6: Official Report Assistance
- Once the user's immediate technical steps are verified, ask them gently: "Would you like me to prepare an official incident report for you?"
- STOP. Wait for the user's "Yes" or "No".
- If "Yes", call `generate_report_template`. Explain that the template is ready in the dashboard below.
- If "No", simply acknowledge it and proceed to Stage 7.

STAGE 7: Emotional Check-in (Interactive)
- ONLY AFTER Stages 5 and 6 are complete, gently ask the user: "On a scale of 1-10, how helpless or scared do you feel right now?"
- STOP. Wait for the user to reply with a number.
- After the user replies with their score, call `emotional_checkin(category, score)`.
- Provide warm validation based on that score and offer the resilience exercise. Ask if they need anything else.

RULES:
- Detect the user's language (English or Swahili) from their message and respond entirely in that same language.
- DO NOT list raw XML/tool code outputs in your conversational text.
- Be highly conversational!
"""
    sys_msg = SystemMessage(content=sys_msg_text)
    
    response = llm_with_tools.invoke([sys_msg] + state["messages"])
    
    return {"messages": [response]}


def custom_tool_node(state: AgentState):
    """Executes the tool calls and captures any state updates they yield."""
    last_message = state["messages"][-1]
    
    tool_msgs = []
    state_updates = {}
    
    language = state.get("language", "en")
    
    for tool_call in last_message.tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        call_id = tool_call["id"]
        
        try:
            if name == "classify_incident":
                res, updates = run_classify_incident(**args)
                tool_msgs.append(ToolMessage(content=res, tool_call_id=call_id))
                state_updates.update(updates)
                state_updates["current_stage"] = "2_technical"
                
            elif name == "get_technical_playbook":
                res, updates = run_get_technical_playbook(category=args.get("category", "unknown"), language=language)
                tool_msgs.append(ToolMessage(content=res, tool_call_id=call_id))
                state_updates.update(updates)
                
            elif name == "generate_report_template":
                res, updates = run_generate_report_template(
                    user_summary=args.get("user_summary", ""), 
                    category=args.get("category", "unknown"),
                    language=language
                )
                tool_msgs.append(ToolMessage(content=res, tool_call_id=call_id))
                state_updates.update(updates)
                state_updates["current_stage"] = "4_emotional"
                
            elif name == "emotional_checkin":
                res, updates = run_emotional_checkin(
                    category=args.get("category", "unknown"), 
                    score=args.get("score", 5),
                    language=language
                )
                tool_msgs.append(ToolMessage(content=res, tool_call_id=call_id))
                state_updates.update(updates)
                
            else:
                tool_msgs.append(ToolMessage(content=f"Error: Unknown tool {name}", tool_call_id=call_id))
                
        except Exception as e:
            tool_msgs.append(ToolMessage(content=f"Error executing tool {name}: {str(e)}", tool_call_id=call_id))
            
    return {"messages": tool_msgs, **state_updates}


def should_continue(state: AgentState) -> str:
    """Determine whether to route to the tool node or end."""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# ─────────────────────────────────────────────
# BUILD RE-ACT GRAPH
# ─────────────────────────────────────────────
def build_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", custom_tool_node)
    
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

# ─────────────────────────────────────────────
# PUBLIC RUNNER
# ─────────────────────────────────────────────
def get_compiled_agent():
    return build_agent()
