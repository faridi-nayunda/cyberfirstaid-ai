"""
CyberFirstAid AI - Streamlit Interface
Conversational ReAct Agent UI with Dynamic Dashboard Cards
Full bilingual (Swahili/English) UI following the rigorous LangGraph agent state progression
"""

import streamlit as st
import os
import sys
import time
import re
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import get_compiled_agent

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CyberFirstAid AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# TRANSLATIONS
# ─────────────────────────────────────────────
T = {
    "en": {
        "title": "🛡️ CyberFirstAid AI",
        "tagline": "Immediate help after a cyber attack — For Tanzania",
        "sidebar_title": "Settings",
        "language_label": "Interface Language",
        "api_key_label": "Groq API Key",
        "api_key_help": "Get your free key at console.groq.com",
        "chat_placeholder": "Type your message here (e.g., 'My phone was hacked')...",
        "section_classification": "🔍 Incident Classification",
        "section_technical": "🛠️ Technical Recovery Steps",
        "section_report": "📝 Official Incident Report",
        "section_instructions": "📤 How to Submit",
        "section_emotional": "💙 Emotional Support",
        "severity_label": "Severity",
        "category_label": "Incident Type",
        "channel_label": "Recommended Reporting Channel",
        "disclaimer": "⚠️ CyberFirstAid AI is not a substitute for professional legal or mental health support. Privacy-first design — no data is stored.",
        "wsis_badge": "✅ Aligned with WSIS C4, C5, C10 | SDG 4, 9, 10, 16",
        "clear_chat": "🗑️ Clear Conversation",
        "severity_colors": {"critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium", "low": "🟢 Low"},
        "category_names": {
            "full_device_compromise": "Full Device Compromise / Remote Control",
            "airtel_money_scam": "Airtel Money Scam",
            "mpesa_scam": "M-Pesa Scam",
            "tigo_pesa_scam": "Tigo Pesa Scam",
            "account_takeover": "Account Takeover (WhatsApp / Facebook / Email)",
            "malware_infection": "Malware / Virus Infection",
            "data_breach": "Data Breach / Credentials Leaked",
            "unknown": "Unknown / General Incident"
        },
        "critical_warning": "⚠️ CRITICAL: If your device is fully compromised — Do NOT use it for sensitive actions. Switch to a borrowed device and continue here.",
    },
    "sw": {
        "title": "🛡️ CyberFirstAid AI",
        "tagline": "Msaada wa haraka baada ya shambulio la mtandao — Kwa Tanzania",
        "sidebar_title": "Mipangilio",
        "language_label": "Lugha ya Kiolesura",
        "api_key_label": "Ufunguo wa Groq API",
        "api_key_help": "Pata ufunguo wako wa bure kwenye console.groq.com",
        "chat_placeholder": "Andika ujumbe wako hapa (mf. 'Simu yangu imedhibitiwa')...",
        "section_classification": "🔍 Utambuzi wa Tukio",
        "section_technical": "🛠️ Hatua za Uokoaji wa Kiufundi",
        "section_report": "📝 Ripoti Rasmi ya Tukio",
        "section_instructions": "📤 Jinsi ya Kuwasilisha",
        "section_emotional": "💙 Msaada wa Kihisia",
        "severity_label": "Ukali",
        "category_label": "Aina ya Tukio",
        "channel_label": "Kituo Kilichopendekezwa cha Kuripoti",
        "disclaimer": "⚠️ CyberFirstAid AI si mbadala wa msaada wa kisheria au afya ya akili wa kitaalamu. Muundo wa kwanza faragha — hakuna data inayohifadhiwa.",
        "wsis_badge": "✅ Imeoanishwa na WSIS C4, C5, C10 | SDG 4, 9, 10, 16",
        "clear_chat": "🗑️ Futa Mazungumzo",
        "severity_colors": {"critical": "🔴 Mkubwa Sana", "high": "🟠 Mkubwa", "medium": "🟡 Wastani", "low": "🟢 Ndogo"},
        "category_names": {
            "full_device_compromise": "Udhibiti Kamili wa Kifaa / Udhibiti wa Mbali",
            "airtel_money_scam": "Udanganyifu wa Airtel Money",
            "mpesa_scam": "Udanganyifu wa M-Pesa",
            "tigo_pesa_scam": "Udanganyifu wa Tigo Pesa",
            "account_takeover": "Kuchukuliwa kwa Akaunti (WhatsApp / Facebook / Barua pepe)",
            "malware_infection": "Virusi / Maambukizi ya Programu Hasidi",
            "data_breach": "Uvunjaji wa Data / Taarifa Zilizovuja",
            "unknown": "Haijulikani / Tukio la Jumla"
        },
        "critical_warning": "⚠️ MUHIMU: Kama kifaa chako kimechukuliwa kabisa — USITUMIE kwa vitendo vya siri. Badilisha kwenye kifaa kilichokopwa na endelea hapa.",
    }
}


# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f0f7ff; }
        .cyber-header {
            background: linear-gradient(135deg, #1a5276 0%, #2980b9 50%, #27ae60 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(41,128,185,0.2);
        }
        .cyber-header h1 { margin: 0; font-size: 2rem; font-weight: 800; }
        .cyber-header p { margin: 0.2rem 0 0; font-size: 1rem; opacity: 0.92; }
        .tech-step {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 0.7rem 1rem;
            margin: 0.4rem 0;
            font-size: 0.95rem;
            border: 1px solid #e9ecef;
        }
        .step-card {
            background: white;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            margin: 1rem 0;
            border-left: 5px solid #2980b9;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        }
        .step-card.emotional { border-left-color: #8e44ad; background: #fdf5ff; }
        .wsis-badge {
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.4);
            border-radius: 20px;
            padding: 0.3rem 0.9rem;
            font-size: 0.8rem;
            display: inline-block;
            margin-top: 0.5rem;
        }
        .critical-warning {
            background: #fff3cd;
            border: 2px solid #e74c3c;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 0.8rem 0;
            font-weight: 600;
            color: #c0392b;
        }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER COMPONENTS
# ─────────────────────────────────────────────
def render_header(lang):
    t = T[lang]
    st.markdown(f"""
    <div class="cyber-header">
        <h1>{t['title']}</h1>
        <p>{t['tagline']}</p>
        <div class="wsis-badge">{t['wsis_badge']}</div>
    </div>
    """, unsafe_allow_html=True)

def severity_badge(severity, lang):
    return T[lang]["severity_colors"].get(severity, severity)

def category_name(category, lang):
    return T[lang]["category_names"].get(category, category)

def clean_ai_content(content):
    if not content:
        return ""
    # Remove Groq's raw XML-style tool call leakage
    cleaned = re.sub(r"<function=.*?>.*?</function>", "", content, flags=re.DOTALL)
    cleaned = re.sub(r"<tool_call>.*?</tool_call>", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()

# ─────────────────────────────────────────────
# INITIALIZE STATE
# ─────────────────────────────────────────────
def init_agent_state(lang):
    return {
        "messages": [
            AIMessage(content="Hello. I am CyberFirstAid AI. How can I help you today? Do you need to report a cyber incident?" if lang == "en" else "Hujambo. Mimi ni msaidizi wa CyberFirstAid AI. Nikusaidie nini leo? Je, unahitaji kuripoti tukio la kimtandao?")
        ],
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


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    inject_css()

    # ── SIDEBAR ──────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Settings / Mipangilio")
        lang = st.selectbox(
            "🌐 Language / Lugha",
            options=["en", "sw"],
            format_func=lambda x: "English" if x == "en" else "Kiswahili",
            key="language_select"
        )
        t = T[lang]

        api_key = st.text_input(
            t["api_key_label"],
            type="password",
            help=t["api_key_help"],
            key="api_key_input"
        )
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key

        st.markdown("---")
        if st.button(t["clear_chat"], use_container_width=True):
            st.session_state.agent_state = init_agent_state(lang)
            st.rerun()

    # ── HEADER & INIT ────────────────────────
    render_header(lang)

    if not os.environ.get("GROQ_API_KEY"):
        st.warning("🔑 Please enter your Groq API key in the sidebar to get started.")
        return

    if "agent_state" not in st.session_state:
        st.session_state.agent_state = init_agent_state(lang)

    # Sync state variables dynamically over simple inputs
    st.session_state.agent_state["language"] = lang

    state = st.session_state.agent_state

    # ── CHAT HISTORY & DYNAMIC DASHBOARD ─────
    col1, col2 = st.columns([1.1, 1.4])
    
    with col1:
        st.markdown("### 💬 Conversation")
        chat_container = st.container(height=550)
        
        # Display chat messages (filtering out Tool calls and Tool messages for clean UI)
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                with chat_container.chat_message("user"):
                    st.write(msg.content)
            elif isinstance(msg, AIMessage):
                cleaned_text = clean_ai_content(msg.content)
                if cleaned_text:
                    with chat_container.chat_message("assistant"):
                        st.write(cleaned_text)

        # ── CHAT INPUT ───────────────────────
        if prompt := st.chat_input(t["chat_placeholder"]):
            # Add user message to state
            state["messages"].append(HumanMessage(content=prompt))
            with chat_container.chat_message("user"):
                st.write(prompt)

            # Invoke Agent
            with chat_container.chat_message("assistant"):
                with st.spinner("CyberFirstAid is thinking..."):
                    agent = get_compiled_agent()
                    # Run the agent
                    new_state = agent.invoke(state)
                    # Update session state with the new full state returned
                    st.session_state.agent_state = new_state
                    
                    # Output the latest assistant message(s) that have content
                    for msg in new_state["messages"][len(state["messages"]):]:
                        if isinstance(msg, AIMessage):
                            cleaned_text = clean_ai_content(msg.content)
                            if cleaned_text:
                                st.write(cleaned_text)
            st.rerun()

    # ── UI DASHBOARD (populated by tools) ────
    with col2:
        st.markdown("### 📋 Incident Dashboard")
        
        if state.get("incident_severity") == "critical":
            st.markdown(f"""<div class="critical-warning">{t['critical_warning']}</div>""", unsafe_allow_html=True)

        if not state.get("incident_category"):
            st.info("The dashboard will update automatically as the assistant classifies your incident and generates steps.")

        # 1. Classification Card
        if state.get("incident_category"):
            with st.expander(t["section_classification"], expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.metric(t["category_label"], category_name(state["incident_category"], lang))
                with c2:
                    st.metric(t["severity_label"], severity_badge(state["incident_severity"], lang))
                
                channels = state.get("recommended_channels") or ["tzcert"]
                st.metric(t["channel_label"], ", ".join(channels).upper())
                
                if state.get("classification_reasoning"):
                    st.caption(f"💡 {state['classification_reasoning']}")

        # 2. Technical Steps Card
        if state.get("technical_steps"):
            with st.expander(t["section_technical"], expanded=True):
                if state.get("technical_summary"):
                    st.markdown(state["technical_summary"])
                for i, step in enumerate(state["technical_steps"], 1):
                    st.markdown(f"""<div class="tech-step"><b>{i}.</b> {step}</div>""", unsafe_allow_html=True)

        # 3. Report Card
        if state.get("report_template") and state.get("wants_report"):
            with st.expander(t["section_report"], expanded=True):
                st.success("✅ Your report template is ready.")
                
                tzcert = state.get("tzcert_fields", {})
                if lang == "sw":
                    st.markdown("#### 📋 Thamani za Kuchagua (Dropdowns)")
                else:
                    st.markdown("#### 📋 Values to Select (Dropdowns)")
                
                rc1, rc2, rc3 = st.columns(3)
                with rc1: st.info(f"**TYPE:** `{tzcert.get('type','Incident')}`")
                with rc2: st.info(f"**SUBJECT:** `{tzcert.get('subject','')}`")
                with rc3: st.info(f"**CATEGORY:** `{tzcert.get('category','')}`")

                st.markdown("#### ✍️ Message to Copy")
                # Extract the core message logic to present it nicely
                template = state["report_template"]
                if "──────" in template:
                    parts = template.split("──────────────────────────────────────────────────────────────")
                    msg_body = parts[2].strip() if len(parts) > 2 else template
                else:
                    msg_body = template

                st.code(msg_body, language=None)
                
                if state.get("submission_instructions"):
                    st.markdown(state["submission_instructions"])

        # 4. Emotional Check-in Card
        if state.get("emotional_response"):
            with st.expander(t["section_emotional"], expanded=True):
                st.markdown(f"""<div class="step-card emotional" style="margin-top:0;">{state['emotional_response']}</div>""", unsafe_allow_html=True)
                if state.get("resilience_exercise"):
                    st.markdown("---")
                    st.markdown(state["resilience_exercise"])


if __name__ == "__main__":
    main()
