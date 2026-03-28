"""
CyberFirstAid AI - Streamlit Interface
Full bilingual (Swahili/English) UI following the LangGraph flow diagram
"""

import streamlit as st
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import run_agent

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
        "incident_header": "🚨 Describe What Happened",
        "incident_placeholder": "Describe your cyber incident in English or Swahili...\n\nExamples:\n• My phone is being controlled by someone\n• I was scammed via M-Pesa voice call\n• My WhatsApp account was taken over\n• I found strange apps on my phone",
        "quick_incidents": "Quick Start — Select your situation:",
        "submit_btn": "🆘 Get Immediate Help",
        "step1": "🔍 Classifying your incident...",
        "step2": "📡 Determining reporting channels...",
        "step3": "🛠️ Preparing recovery steps...",
        "step4": "📝 Generating report template...",
        "step5": "💙 Preparing emotional support...",
        "section_classification": "🔍 Incident Classification",
        "section_technical": "🛠️ Technical Recovery Steps",
        "section_report": "📝 Direct Report Assistant",
        "section_template": "📋 Your Ready-to-Submit Report",
        "section_instructions": "📤 How to Submit",
        "section_emotional": "💙 How Are You Feeling?",
        "severity_label": "Severity",
        "category_label": "Incident Type",
        "channel_label": "Recommended Reporting Channel",
        "helplessness_label": "On a scale of 1–10, how helpless or scared do you feel right now?",
        "helplessness_help": "1 = Calm and in control | 10 = Extremely overwhelmed",
        "copy_hint": "📋 Copy the report below and paste into the official form:",
        "wants_report_label": "Would you like me to prepare your official report?",
        "wants_report_yes": "Yes, prepare my report",
        "wants_report_no": "No, just the recovery steps",
        "confidence_before": "Your helplessness score when you arrived",
        "confidence_after": "Your helplessness score now (enter after reading)",
        "confidence_improvement": "📈 Helplessness reduced by",
        "disclaimer": "⚠️ CyberFirstAid AI is not a substitute for professional legal or mental health support. Privacy-first design — no data is stored.",
        "wsis_badge": "✅ Aligned with WSIS C4, C5, C10 | SDG 4, 9, 10, 16",
        "new_incident": "🔄 Start New Incident",
        "severity_colors": {"critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium", "low": "🟢 Low"},
        "category_names": {
            "full_device_compromise": "Full Device Compromise / Remote Control",
            "mobile_money_scam": "Mobile Money Scam (M-Pesa / Airtel / Tigo)",
            "account_takeover": "Account Takeover (WhatsApp / Facebook / Email)",
            "malware_infection": "Malware / Virus Infection",
            "data_breach": "Data Breach / Credentials Leaked",
            "unknown": "Unknown / General Incident"
        },
        "quick_options": [
            "My phone is being controlled remotely",
            "I was scammed via M-Pesa / mobile money",
            "My WhatsApp/Facebook account was hacked",
            "I found a virus/strange app on my phone",
            "My personal data was leaked online",
        ],
        "report_ready": "✅ Your report is ready. Review, fill in your personal details, then follow the submission steps below.",
        "no_report_selected": "Skipping report generation as requested.",
        "critical_warning": "⚠️ CRITICAL: If your device is fully compromised — Do NOT use it for sensitive actions. Switch to a borrowed device and continue here.",
    },
    "sw": {
        "title": "🛡️ CyberFirstAid AI",
        "tagline": "Msaada wa haraka baada ya shambulio la mtandao — Kwa Tanzania",
        "sidebar_title": "Mipangilio",
        "language_label": "Lugha ya Kiolesura",
        "api_key_label": "Ufunguo wa Groq API",
        "api_key_help": "Pata ufunguo wako wa bure kwenye console.groq.com",
        "incident_header": "🚨 Eleza Kilichotokea",
        "incident_placeholder": "Eleza tukio lako la mtandao kwa Kiswahili au Kiingereza...\n\nMifano:\n• Simu yangu inaongea peke yake\n• Nilidanganywa kupitia M-Pesa\n• WhatsApp yangu imechukuliwa\n• Nimepata programu za ajabu kwenye simu yangu",
        "quick_incidents": "Anza Haraka — Chagua hali yako:",
        "submit_btn": "🆘 Pata Msaada Mara Moja",
        "step1": "🔍 Inatambua tukio lako...",
        "step2": "📡 Inabainisha njia za kuripoti...",
        "step3": "🛠️ Inaandaa hatua za uokoaji...",
        "step4": "📝 Inatoa kiolezo cha ripoti...",
        "step5": "💙 Inaandaa msaada wa kihisia...",
        "section_classification": "🔍 Utambuzi wa Tukio",
        "section_technical": "🛠️ Hatua za Uokoaji wa Kiufundi",
        "section_report": "📝 Msaidizi wa Ripoti ya Moja kwa Moja",
        "section_template": "📋 Ripoti Yako Tayari Kuwasilishwa",
        "section_instructions": "📤 Jinsi ya Kuwasilisha",
        "section_emotional": "💙 Unajisikiaje?",
        "severity_label": "Ukali",
        "category_label": "Aina ya Tukio",
        "channel_label": "Kituo Kilichopendekezwa cha Kuripoti",
        "helplessness_label": "Kwa kiwango cha 1 hadi 10, unajisikiaje kutokuwa na nguvu au kuogopa sasa hivi?",
        "helplessness_help": "1 = Utulivu na udhibiti | 10 = Umejaa wasiwasi kabisa",
        "copy_hint": "📋 Nakili ripoti hapa chini na ubandike kwenye fomu rasmi:",
        "wants_report_label": "Je, unataka nikuandalie ripoti rasmi?",
        "wants_report_yes": "Ndiyo, niandalie ripoti yangu",
        "wants_report_no": "Hapana, hatua za uokoaji tu",
        "confidence_before": "Kiwango chako cha kutokuwa na nguvu ulipofika",
        "confidence_after": "Kiwango chako cha kutokuwa na nguvu sasa (ingiza baada ya kusoma)",
        "confidence_improvement": "📈 Kutokuwa na nguvu kumepungua kwa",
        "disclaimer": "⚠️ CyberFirstAid AI si mbadala wa msaada wa kisheria au afya ya akili wa kitaalamu. Muundo wa kwanza faragha — hakuna data inayohifadhiwa.",
        "wsis_badge": "✅ Imeoanishwa na WSIS C4, C5, C10 | SDG 4, 9, 10, 16",
        "new_incident": "🔄 Anza Tukio Jipya",
        "severity_colors": {"critical": "🔴 Mkubwa Sana", "high": "🟠 Mkubwa", "medium": "🟡 Wastani", "low": "🟢 Ndogo"},
        "category_names": {
            "full_device_compromise": "Udhibiti Kamili wa Kifaa / Udhibiti wa Mbali",
            "mobile_money_scam": "Udanganyifu wa Pesa za Simu (M-Pesa / Airtel / Tigo)",
            "account_takeover": "Kuchukuliwa kwa Akaunti (WhatsApp / Facebook / Barua pepe)",
            "malware_infection": "Virusi / Maambukizi ya Programu Hasidi",
            "data_breach": "Uvunjaji wa Data / Taarifa Zilizovuja",
            "unknown": "Haijulikani / Tukio la Jumla"
        },
        "quick_options": [
            "Simu yangu inadhibitiwa kwa mbali",
            "Nilidanganywa kupitia M-Pesa / pesa za simu",
            "WhatsApp/Facebook yangu imehackiwa",
            "Nimepata virusi/programu ya ajabu kwenye simu yangu",
            "Taarifa zangu binafsi zimevuja mtandaoni",
        ],
        "report_ready": "✅ Ripoti yako iko tayari. Angalia, jaza taarifa zako binafsi, kisha fuata hatua za uwasilishaji hapa chini.",
        "no_report_selected": "Imetoroka utengenezaji wa ripoti kama ilivyoombwa.",
        "critical_warning": "⚠️ MUHIMU: Kama kifaa chako kimechukuliwa kabisa — USITUMIE kwa vitendo vya siri. Badilisha kwenye kifaa kilichokopwa na endelea hapa.",
    }
}


# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
        /* Main background */
        .stApp { background-color: #f0f7ff; }

        /* Header */
        .cyber-header {
            background: linear-gradient(135deg, #1a5276 0%, #2980b9 50%, #27ae60 100%);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(41,128,185,0.3);
        }
        .cyber-header h1 { margin: 0; font-size: 2.2rem; font-weight: 800; }
        .cyber-header p { margin: 0.3rem 0 0; font-size: 1.05rem; opacity: 0.92; }

        /* Step cards */
        .step-card {
            background: white;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            margin: 1rem 0;
            border-left: 5px solid #2980b9;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        }
        .step-card.critical { border-left-color: #e74c3c; background: #fff5f5; }
        .step-card.high { border-left-color: #e67e22; }
        .step-card.medium { border-left-color: #f1c40f; }
        .step-card.emotional { border-left-color: #8e44ad; background: #fdf5ff; }
        .step-card.report { border-left-color: #27ae60; background: #f0fff4; }

        /* Step header */
        .step-header {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1a5276;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Technical steps list */
        .tech-step {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 0.7rem 1rem;
            margin: 0.4rem 0;
            font-size: 0.95rem;
            border: 1px solid #e9ecef;
        }

        /* Report box */
        .report-box {
            background: #1a1a2e;
            color: #e0e0e0;
            border-radius: 10px;
            padding: 1.2rem;
            font-family: 'Courier New', monospace;
            font-size: 0.88rem;
            line-height: 1.6;
            white-space: pre-wrap;
            margin: 0.8rem 0;
        }

        /* Confidence meter */
        .confidence-bar {
            height: 12px;
            border-radius: 6px;
            background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60);
            margin: 0.5rem 0;
        }

        /* Badge */
        .wsis-badge {
            background: #eaf4fb;
            border: 1px solid #2980b9;
            border-radius: 20px;
            padding: 0.3rem 0.9rem;
            font-size: 0.8rem;
            color: #1a5276;
            display: inline-block;
            margin: 0.3rem 0;
        }

        /* Warning box */
        .critical-warning {
            background: #fff3cd;
            border: 2px solid #e74c3c;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 0.8rem 0;
            font-weight: 600;
            color: #c0392b;
        }

        /* Buttons */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }

        /* Sidebar */
        .css-1d391kg { background: #1a2744; }

        /* Progress flow */
        .flow-progress {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }
        .flow-step {
            background: #ddd;
            border-radius: 20px;
            padding: 0.3rem 0.8rem;
            font-size: 0.8rem;
            color: #555;
        }
        .flow-step.done {
            background: #27ae60;
            color: white;
        }
        .flow-step.active {
            background: #2980b9;
            color: white;
            font-weight: 700;
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
        <div style="margin-top:0.8rem;">
            <span class="wsis-badge" style="background:rgba(255,255,255,0.15);border-color:rgba(255,255,255,0.4);color:white;">
                {t['wsis_badge']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_flow_progress(current_step, lang):
    lang_steps = {
        "en": ["🔍 Classify", "📡 Channel", "🛠️ Recovery", "📝 Report", "💙 Wellbeing"],
        "sw": ["🔍 Tambua", "📡 Kituo", "🛠️ Uokoaji", "📝 Ripoti", "💙 Ustawi"],
    }
    steps = lang_steps[lang]
    html = '<div class="flow-progress">'
    for i, step in enumerate(steps):
        css = "done" if i < current_step else ("active" if i == current_step else "flow-step")
        if i < current_step:
            html += f'<span class="flow-step done">{step}</span>'
        elif i == current_step:
            html += f'<span class="flow-step active">{step}</span>'
        else:
            html += f'<span class="flow-step">{step}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def severity_badge(severity, lang):
    t = T[lang]
    return t["severity_colors"].get(severity, severity)


def category_name(category, lang):
    t = T[lang]
    return t["category_names"].get(category, category)


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

        st.markdown("---")
        api_key = st.text_input(
            T[lang]["api_key_label"],
            type="password",
            help=T[lang]["api_key_help"],
            key="api_key_input"
        )
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("✅ API Key set!" if lang == "en" else "✅ Ufunguo umewekwa!")

        st.markdown("---")
        st.markdown("""
        <div style='font-size:0.8rem;color:#888;'>
        <b>CyberFirstAid AI</b><br>
        iSAFE Hackathon 2026<br>
        CyberPeace Institute × WSIS<br><br>
        Challenge 2: Defend the Digital Citizen
        </div>
        """, unsafe_allow_html=True)

    t = T[lang]

    # ── HEADER ───────────────────────────────
    render_header(lang)

    # Check API key
    if not os.environ.get("GROQ_API_KEY"):
        st.warning(
            "🔑 Please enter your Groq API key in the sidebar to get started. Get a free key at console.groq.com"
            if lang == "en" else
            "🔑 Tafadhali ingiza ufunguo wako wa Groq API kwenye upande wa pembeni kuanza. Pata ufunguo wa bure kwenye console.groq.com"
        )
        return

    # ── SESSION STATE ────────────────────────
    if "result" not in st.session_state:
        st.session_state.result = None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "confidence_after" not in st.session_state:
        st.session_state.confidence_after = None

    # ── INCIDENT INPUT ────────────────────────
    if not st.session_state.submitted:
        st.markdown(f"### {t['incident_header']}")

        # Quick start buttons
        st.markdown(f"**{t['quick_incidents']}**")
        quick_cols = st.columns(len(t["quick_options"]))
        quick_selected = None
        for i, (col, opt) in enumerate(zip(quick_cols, t["quick_options"])):
            with col:
                if st.button(opt, key=f"quick_{i}", use_container_width=True):
                    quick_selected = opt

        user_message = st.text_area(
            label="",
            placeholder=t["incident_placeholder"],
            height=160,
            key="user_message",
            value=quick_selected or "",
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            helplessness_score = st.slider(
                t["helplessness_label"],
                min_value=1, max_value=10, value=5,
                help=t["helplessness_help"],
                key="helplessness_slider"
            )
            # Emoji feedback
            emoji_map = {1:"😌", 2:"🙂", 3:"😐", 4:"😟", 5:"😕", 6:"😧", 7:"😨", 8:"😰", 9:"😱", 10:"😭"}
            st.markdown(f"<div style='font-size:2rem;text-align:center'>{emoji_map.get(helplessness_score, '😐')}</div>", unsafe_allow_html=True)

        with col2:
            wants_report = st.radio(
                t["wants_report_label"],
                options=[True, False],
                format_func=lambda x: t["wants_report_yes"] if x else t["wants_report_no"],
                key="wants_report",
                horizontal=True,
            )

        if st.button(t["submit_btn"], type="primary", use_container_width=True, disabled=not user_message.strip()):
            with st.spinner(""):
                # Animated steps
                progress_placeholder = st.empty()
                steps = [t["step1"], t["step2"], t["step3"], t["step4"], t["step5"]]
                for i, step_msg in enumerate(steps):
                    with progress_placeholder.container():
                        render_flow_progress(i, lang)
                        st.info(step_msg)
                    time.sleep(0.4)

                # Run the agent
                result = run_agent(
                    user_message=user_message,
                    language=lang,
                    helplessness_score=helplessness_score,
                    wants_report=wants_report,
                )
                st.session_state.result = result
                st.session_state.submitted = True
                progress_placeholder.empty()
                st.rerun()

    # ── RESULTS ──────────────────────────────
    if st.session_state.submitted and st.session_state.result:
        result = st.session_state.result

        # Flow progress — complete
        render_flow_progress(5, lang)

        # Critical device warning
        if result.get("incident_severity") == "critical":
            st.markdown(f"""<div class="critical-warning">{t['critical_warning']}</div>""", unsafe_allow_html=True)

        # ── SECTION 1: CLASSIFICATION ─────────
        with st.expander(t["section_classification"], expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    t["category_label"],
                    category_name(result.get("incident_category", "unknown"), lang)
                )
            with col2:
                st.metric(
                    t["severity_label"],
                    severity_badge(result.get("incident_severity", "medium"), lang)
                )
            with col3:
                channels = result.get("recommended_channels", ["tzcert"])
                st.metric(
                    t["channel_label"],
                    ", ".join(channels).upper()
                )
            if result.get("classification_reasoning"):
                st.info(result["classification_reasoning"])

        # ── SECTION 2: TECHNICAL STEPS ────────
        with st.expander(t["section_technical"], expanded=True):
            severity = result.get("incident_severity", "medium")
            card_class = "critical" if severity == "critical" else severity

            if result.get("technical_summary"):
                st.markdown(result["technical_summary"])

            steps = result.get("technical_steps", [])
            for i, step in enumerate(steps, 1):
                st.markdown(f"""<div class="tech-step"><b>{i}.</b> {step}</div>""", unsafe_allow_html=True)

        # ── SECTION 3: REPORT ASSISTANT ────────
        with st.expander(t["section_report"], expanded=True):
            if result.get("wants_report"):
                st.success(t["report_ready"])

                # ── Step A: Form values reference card (dropdowns to select)
                tzcert = result.get("tzcert_fields", {})
                if tzcert:
                    if lang == "sw":
                        st.markdown("#### 📋 Thamani za Kuchagua kwenye Fomu")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**AINA**\n\n`{tzcert.get('type','Incident')}`")
                        with col2:
                            st.markdown(f"**MADA (Subject)**\n\n`{tzcert.get('subject','')}`")
                        with col3:
                            st.markdown(f"**KATEGORIA (Category)**\n\n`{tzcert.get('category','')}`")
                        st.caption(f"💡 Mada: {tzcert.get('subject_note_sw','')}")
                        st.caption(f"💡 Kategoria: {tzcert.get('category_note_sw','')}")
                    else:
                        st.markdown("#### 📋 Dropdown Values to Select on the Form")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**TYPE**\n\n`{tzcert.get('type','Incident')}`")
                        with col2:
                            st.markdown(f"**SUBJECT**\n\n`{tzcert.get('subject','')}`")
                        with col3:
                            st.markdown(f"**CATEGORY**\n\n`{tzcert.get('category','')}`")
                        st.caption(f"💡 Subject: {tzcert.get('subject_note_en','')}")
                        st.caption(f"💡 Category: {tzcert.get('category_note_en','')}")

                st.divider()

                # ── Step B: The message to copy (only the message body, not the whole template)
                template = result.get("report_template", "")
                if template:
                    # Extract just the message body between the two dashed lines
                    if "──────" in template:
                        parts = template.split("──────────────────────────────────────────────────────────────")
                        # parts[1] is the label line, parts[2] is the message body, parts[3] is the footer
                        msg_body = parts[2].strip() if len(parts) > 2 else template
                    else:
                        msg_body = template

                    if lang == "sw":
                        st.markdown("#### ✍️ Ujumbe wa Kunakili (Bandika kwenye uwanja wa 'Message')")
                        st.info("👆 Nakili ujumbe wote hapa chini kama ulivyo, kisha ubandike kwenye uwanja wa 'Message' kwenye fomu ya TZ-CERT.")
                    else:
                        st.markdown("#### ✍️ Message to Copy (Paste into the 'Message' field)")
                        st.info("👆 Copy the entire message below as-is, then paste it into the 'Message' field on the TZ-CERT form.")

                    st.code(msg_body, language=None)

                st.divider()

                # ── Step C: How to submit (steps only, no repeated template)
                if result.get("submission_instructions"):
                    st.markdown(result["submission_instructions"])
            else:
                st.info(t["no_report_selected"])

        # ── SECTION 4: EMOTIONAL CHECK-IN ──────
        with st.expander(t["section_emotional"], expanded=True):
            score_before = result.get("confidence_before", 5)

            # Emotional response from LLM
            if result.get("emotional_response"):
                st.markdown(f"""<div class="step-card emotional">{result['emotional_response']}</div>""", unsafe_allow_html=True)

            # Resilience exercise
            if result.get("resilience_exercise"):
                st.markdown(result["resilience_exercise"])

            st.markdown("---")

            # Before score
            st.metric(
                t["confidence_before"],
                f"{score_before}/10",
                delta=None
            )

            # After score input
            after_score = st.slider(
                t["confidence_after"],
                min_value=1, max_value=10,
                value=st.session_state.confidence_after or max(1, score_before - 2),
                key="after_slider"
            )
            st.session_state.confidence_after = after_score

            # Improvement calculation
            improvement = score_before - after_score
            if improvement > 0:
                pct = round((improvement / score_before) * 100)
                st.success(f"{t['confidence_improvement']} {pct}% ({score_before} → {after_score})")
            elif improvement == 0:
                st.info("📊 Score unchanged — that's okay, recovery takes time." if lang == "en" else "📊 Kiwango hakijabadilika — hiyo ni sawa, kupona kunachukua muda.")
            else:
                st.warning("📊 This is still processing — give yourself a moment." if lang == "en" else "📊 Bado inachakatwa — jipe muda kidogo.")

        # ── DISCLAIMER & NEW INCIDENT ──────────
        st.markdown(f"<div style='font-size:0.82rem;color:#888;margin-top:1rem;'>{t['disclaimer']}</div>", unsafe_allow_html=True)

        if st.button(t["new_incident"], type="secondary"):
            st.session_state.result = None
            st.session_state.submitted = False
            st.session_state.confidence_after = None
            st.rerun()


if __name__ == "__main__":
    main()
