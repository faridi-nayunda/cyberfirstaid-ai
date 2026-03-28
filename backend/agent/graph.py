"""
CyberFirstAid AI - LangGraph Agentic Workflow
Nodes follow the flow diagram exactly:
User Message → Classify Incident → Determine Best Reporting Channel →
Technical Recovery Steps → Direct Report Assistant → Generate Template →
Copy-Paste + Submission Instructions → Trauma-Informed Emotional Check-in

TZ-CERT form fields mapped exactly from https://www.tzcert.go.tz/incident/report
"""

import json
import os
from typing import TypedDict, Optional, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# ─────────────────────────────────────────────
# TZ-CERT EXACT FORM FIELD DEFINITIONS
# Sourced directly from tzcert.go.tz/incident/report
# ─────────────────────────────────────────────

TZCERT_TYPE_OPTIONS = ["Incident", "Vulnerability", "Child Abuse"]

TZCERT_SUBJECT_OPTIONS = [
    "Abusive Content",
    "Malicious Code",
    "Information Gathering",
    "Intrusion Attempts",
    "Intrusions",
    "Information Security",
    "Fraud",
    "Escalation",
    "Others",
]

TZCERT_CATEGORY_OPTIONS = [
    "Spam",
    "Cyberbullying",
    "Child sex/violence",
    "Virus",
    "Worm",
    "Trojan",
    "Spyware",
    "Dialer",
    "Scanning",
    "Sniffing",
    "Social Engineering",
    "Exploitation of known vulnerability",
    "Exploitation of unknown vulnerability",
    "Connection Attempts",
    "New Signature Attacks",
    "Compromise Privileged Account",
    "Compromise unprivileged account",
    "Request Compromise",
    "DDoS",
    "Unauthorized access to information",
    "Unauthorized Modification of Information",
    "Unauthorized Use of Resources",
    "Ransomware",
    "Phishing",
    "All Incidents that do not fit in one of the above categories",
]

# ─────────────────────────────────────────────
# INCIDENT → TZ-CERT FIELD MAPPING
# Maps each CyberFirstAid incident type to the
# correct TZ-CERT Type, Subject, and Category
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
    "mobile_money_scam": {
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
        "category_note_en": "Select 'Trojan' for RAT/spyware/hidden malware. If ransomware locked your files, select 'Ransomware' instead.",
        "category_note_sw": "Chagua 'Trojan' kwa RAT/spyware/programu hasidi iliyofichwa. Kama ransomware ilifunga faili zako, chagua 'Ransomware' badala yake.",
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
# 1. SHARED STATE
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    user_message: str
    language: str
    conversation_history: List[dict]
    incident_category: Optional[str]
    incident_severity: Optional[str]
    classification_reasoning: Optional[str]
    recommended_channels: Optional[List[str]]
    chosen_channel: Optional[str]
    wants_report: Optional[bool]
    technical_steps: Optional[List[str]]
    technical_summary: Optional[str]
    tzcert_fields: Optional[dict]
    report_template: Optional[str]
    submission_instructions: Optional[str]
    helplessness_score: Optional[int]
    emotional_response: Optional[str]
    resilience_exercise: Optional[str]
    confidence_before: Optional[int]
    confidence_after: Optional[int]
    next_node: Optional[str]
    final_output: Optional[str]
    error: Optional[str]


# ─────────────────────────────────────────────
# 2. HELPERS
# ─────────────────────────────────────────────
def load_playbooks() -> dict:
    data_path = os.path.join(os.path.dirname(__file__), "../data/playbooks.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        temperature=0.3,
        max_tokens=1200,
    )


# ─────────────────────────────────────────────
# 3. NODE: CLASSIFY INCIDENT
# ─────────────────────────────────────────────
def classify_incident_node(state: AgentState) -> AgentState:
    llm = get_llm()
    lang = state.get("language", "en")
    user_msg = state["user_message"]

    system_prompt = """You are a cybersecurity incident classifier for CyberFirstAid AI — helping Tanzania citizens after cyber attacks.

Classify into ONE category:
- full_device_compromise: Phone/device remotely controlled, RAT, attacker has full access
- mobile_money_scam: M-Pesa/Airtel/Tigo fraud, voice call scam, money lost via mobile
- account_takeover: WhatsApp/Facebook/email/social media account hacked or taken over
- malware_infection: Virus, spyware, ransomware, suspicious apps, strange phone behavior
- data_breach: Personal data/credentials leaked or exposed
- unknown: Cannot determine

User may write in Swahili, English, or both.

Respond ONLY in this JSON (no markdown):
{"category": "id", "severity": "low|medium|high|critical", "reasoning": "1-sentence in user's language", "language_detected": "en|sw"}"""

    try:
        resp = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Classify: {user_msg}"),
        ])
        raw = resp.content.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        state["incident_category"] = result.get("category", "unknown")
        state["incident_severity"] = result.get("severity", "medium")
        state["classification_reasoning"] = result.get("reasoning", "")
        if lang == "auto":
            state["language"] = result.get("language_detected", "en")
    except Exception as e:
        state["incident_category"] = "unknown"
        state["incident_severity"] = "medium"
        state["classification_reasoning"] = ""
        state["error"] = f"Classification error: {e}"
    return state


# ─────────────────────────────────────────────
# 4. NODE: DETERMINE REPORTING CHANNEL
# ─────────────────────────────────────────────
def determine_reporting_channel_node(state: AgentState) -> AgentState:
    playbooks = load_playbooks()
    category = state.get("incident_category", "unknown")
    matched = next((i for i in playbooks["incident_types"] if i["id"] == category), None)
    if matched:
        state["recommended_channels"] = matched["reporting_channels"]
        state["chosen_channel"] = matched["reporting_channels"][0]
    else:
        state["recommended_channels"] = ["tzcert", "police"]
        state["chosen_channel"] = "tzcert"
    return state


# ─────────────────────────────────────────────
# 5. NODE: TECHNICAL RECOVERY STEPS
# ─────────────────────────────────────────────
def technical_recovery_node(state: AgentState) -> AgentState:
    playbooks = load_playbooks()
    category = state.get("incident_category", "unknown")
    severity = state.get("incident_severity", "medium")
    lang = state.get("language", "en")
    llm = get_llm()

    matched = next((i for i in playbooks["incident_types"] if i["id"] == category), None)
    if matched:
        steps_key = "technical_steps_sw" if lang == "sw" else "technical_steps_en"
        state["technical_steps"] = matched.get(steps_key, matched.get("technical_steps_en", []))
        n = len(state["technical_steps"])
        prompt = (
            f"Andika utangulizi mfupi wa huruma (sentensi 2) kwa mtu aliyepitia '{category}' (ukali: {severity}). "
            f"Sema kwa utulivu: fuata hatua {n} hizi. Kuwa mwenye joto. Kiswahili tu."
            if lang == "sw" else
            f"Write a short compassionate intro (2 sentences) for someone experiencing '{category}' (severity: {severity}). "
            f"Calmly say: please follow these {n} steps. Be warm. English only."
        )
        try:
            state["technical_summary"] = llm.invoke([HumanMessage(content=prompt)]).content.strip()
        except Exception:
            state["technical_summary"] = (
                f"Ninaelewa hali hii ni ngumu. Hapa kuna hatua {n} za kukusaidia."
                if lang == "sw" else
                f"I understand this is difficult. Here are {n} steps to help you recover."
            )
    else:
        state["technical_steps"] = (
            ["Tafadhali nipe maelezo zaidi kuhusu kilichotokea."] if lang == "sw"
            else ["Please describe what happened in more detail so I can provide accurate help."]
        )
        state["technical_summary"] = (
            "Nipe maelezo zaidi ili nikusaidie ipasavyo." if lang == "sw"
            else "Please provide more details so I can help you properly."
        )
    return state


# ─────────────────────────────────────────────
# 6. NODE: DIRECT REPORT ASSISTANT
# ─────────────────────────────────────────────
def direct_report_assistant_node(state: AgentState) -> AgentState:
    if state.get("wants_report") is None:
        state["wants_report"] = True
    return state


# ─────────────────────────────────────────────
# 7. NODE: GENERATE REPORT TEMPLATE
#    Exact TZ-CERT form fields mapped
# ─────────────────────────────────────────────
def generate_report_template_node(state: AgentState) -> AgentState:
    llm = get_llm()
    lang = state.get("language", "en")
    category = state.get("incident_category", "unknown")
    user_msg = state["user_message"]
    severity = state.get("incident_severity", "medium")

    tzcert_map = TZCERT_FIELD_MAP.get(category, TZCERT_FIELD_MAP["unknown"])
    state["tzcert_fields"] = tzcert_map

    # ── Generate the Message field body ──
    # Written in first-person as if the user wrote it themselves.
    # Ownership: "I", "my", "me" — not "the user" or third-party language.
    if lang == "sw":
        msg_prompt = (
            f"Andika ujumbe wa ripoti ya tukio kama ilivyoandikwa na mtu mwenyewe kwa maneno yake.\n"
            f"Mtumiaji alisema hivi: \"{user_msg}\"\n"
            f"Aina ya tukio: {category} (ukali: {severity})\n\n"
            f"MUHIMU — Sheria za uandishi:\n"
            f"- Andika kwa nafsi ya kwanza: 'Mimi', 'yangu', 'nilikuwa', 'niliona'\n"
            f"- USITUMIE lugha ya mawakala au mfumo. Mfano mbaya: 'Mtumiaji anaripoti...'\n"
            f"- Sauti lazima isikike kama mtu wa kawaida anayeeleza tatizo lake\n"
            f"- Muundo wa aya 3: (1) kilichotokea na wakati, (2) athari ninayoiona, "
            f"(3) hatua nilizochukua na msaada ninaouomba\n"
            f"- Kiswahili cha kawaida lakini cha heshima. Hakuna kichwa cha habari."
        )
    else:
        msg_prompt = (
            f"Write an incident report message as if the person is writing it themselves in their own words.\n"
            f"What the user described: \"{user_msg}\"\n"
            f"Incident type: {category} (severity: {severity})\n\n"
            f"IMPORTANT — Writing rules:\n"
            f"- Write in first person: 'I', 'my', 'me', 'I noticed', 'I believe'\n"
            f"- DO NOT use agent or system language. Bad example: 'The user reports...'\n"
            f"- The voice must sound like a real person describing their own problem\n"
            f"- 3-paragraph structure: (1) what happened and when, (2) the impact I am experiencing, "
            f"(3) steps I have already taken and what help I am requesting\n"
            f"- Plain but respectful English. No heading."
        )

    try:
        message_body = llm.invoke([HumanMessage(content=msg_prompt)]).content.strip()
    except Exception as e:
        # Fallback also uses first-person voice
        message_body = (
            f"Ninaandika kuripoti tukio la '{category}' ambalo nililipitia hivi karibuni. "
            f"{user_msg}. Naomba TZ-CERT inisaidie kuchunguza na kunipa mwongozo."
            if lang == "sw" else
            f"I am writing to report a '{category}' incident that I recently experienced. "
            f"{user_msg}. I kindly request TZ-CERT's assistance in investigating this matter."
        )
        state["error"] = str(e)

    # ── Build the TZ-CERT form guide ──
    # NOTE: The template shows ONLY the form fields + the message to copy.
    # Submission steps (how to open the site, click Submit, etc.)
    # are shown SEPARATELY in submission_instructions_node — no duplication.
    if lang == "sw":
        template = f"""╔══════════════════════════════════════════════════════════════╗
║         FOMU YA TZ-CERT — THAMANI ZA KUJAZA                ║
╚══════════════════════════════════════════════════════════════╝

Tumia maadili haya kujaza fomu kwenye tzcert.go.tz:

 AINA      →  ✅ {tzcert_map['type']}
 MADA      →  ✅ {tzcert_map['subject']}
              💡 {tzcert_map['subject_note_sw']}
 KATEGORIA →  ✅ {tzcert_map['category']}
              💡 {tzcert_map['category_note_sw']}

──────────────────────────────────────────────────────────────
 UJUMBE — Nakili kila kitu kati ya mistari miwili hapa chini
──────────────────────────────────────────────────────────────
{message_body}
──────────────────────────────────────────────────────────────
💾 Hifadhi nambari ya kumbukumbu utakayopokea baada ya kutuma."""

    else:
        template = f"""╔══════════════════════════════════════════════════════════════╗
║         TZ-CERT FORM — VALUES TO FILL IN                   ║
╚══════════════════════════════════════════════════════════════╝

Use these values when filling the form on tzcert.go.tz:

 TYPE      →  ✅ {tzcert_map['type']}
 SUBJECT   →  ✅ {tzcert_map['subject']}
              💡 {tzcert_map['subject_note_en']}
 CATEGORY  →  ✅ {tzcert_map['category']}
              💡 {tzcert_map['category_note_en']}

──────────────────────────────────────────────────────────────
 MESSAGE — Copy everything between the two lines below
──────────────────────────────────────────────────────────────
{message_body}
──────────────────────────────────────────────────────────────
💾 Save the reference number you receive after submitting."""

    state["report_template"] = template
    return state


# ─────────────────────────────────────────────
# 8. NODE: SUBMISSION INSTRUCTIONS
# ─────────────────────────────────────────────
def submission_instructions_node(state: AgentState) -> AgentState:
    """
    Provides step-by-step instructions to submit on TZ-CERT (no link duplication —
    the link already appears in the form template above).
    Secondary channels shown ONLY for non-tzcert options (police, mobile provider, etc.).
    """
    playbooks = load_playbooks()
    lang = state.get("language", "en")
    channel = state.get("chosen_channel", "tzcert")
    all_channels = state.get("recommended_channels", [channel])
    tzcert_map = state.get("tzcert_fields", TZCERT_FIELD_MAP["unknown"])

    if lang == "sw":
        instructions = f"""### 📤 Jinsi ya Kutuma Ripoti (Hatua kwa Hatua)

1. **Fungua** 👉 [https://www.tzcert.go.tz/incident/report](https://www.tzcert.go.tz/incident/report)
2. **AINA** — Chagua **"{tzcert_map['type']}"** kwenye menyu
3. **JINA KAMILI** — Jaza jina lako kamili la kweli
4. **SHIRIKA** — Andika **"Individual"** (au jina la shirika lako)
5. **SIMU** — Ingiza nambari yako ya simu (+255...)
6. **BARUA PEPE** — Ingiza barua pepe yako (TZ-CERT watakujibu hapa)
7. **MADA** — Chagua **"{tzcert_map['subject']}"** kwenye menyu
8. **KATEGORIA** — Chagua **"{tzcert_map['category']}"** kwenye menyu
9. **UJUMBE** — Nakili ujumbe kutoka kwenye kisanduku hapo juu → Bandika hapa
10. Angalia kila kitu → Bonyeza **SUBMIT** 🟢

> 💾 Andika nambari yoyote ya kumbukumbu unayopokea baada ya kutuma."""
    else:
        instructions = f"""### 📤 How to Submit (Step by Step)

1. **Open** 👉 [https://www.tzcert.go.tz/incident/report](https://www.tzcert.go.tz/incident/report)
2. **TYPE** — Select **"{tzcert_map['type']}"** from the dropdown
3. **FULL NAME** — Enter your real full name
4. **ORGANIZATION** — Type **"Individual"** (or your organization)
5. **TELEPHONE** — Enter your phone number (+255...)
6. **EMAIL** — Enter your real email (TZ-CERT will reply here)
7. **SUBJECT** — Select **"{tzcert_map['subject']}"** from the dropdown
8. **CATEGORY** — Select **"{tzcert_map['category']}"** from the dropdown
9. **MESSAGE** — Copy the message from the box above → Paste it here
10. Review everything → Click **SUBMIT** 🟢

> 💾 Note down any reference number you receive after submitting."""

    # ── Secondary channels: EXCLUDE tzcert (already handled above).
    # Only add channels that are genuinely different (police, mobile provider, platform).
    NON_TZCERT = {"police", "mobile_money_provider", "platform_report"}
    extra_channels = [ch for ch in all_channels if ch in NON_TZCERT]

    for ch in extra_channels:
        info = playbooks["reporting_channels"].get(ch, {})
        if lang == "sw":
            name = info.get("name_sw", ch)
            contact = info.get("contacts_sw", info.get("contact_sw", info.get("links_sw", "")))
            instr = info.get("instructions_sw", "")
            instructions += f"\n\n---\n### 📞 Pia Ripoti kwa: {name}\n{contact}\n\n_{instr}_"
        else:
            name = info.get("name_en", ch)
            contact = info.get("contacts_en", info.get("contact_en", info.get("links_en", "")))
            instr = info.get("instructions_en", "")
            instructions += f"\n\n---\n### 📞 Also Report to: {name}\n{contact}\n\n_{instr}_"

    state["submission_instructions"] = instructions
    return state


# ─────────────────────────────────────────────
# 9. NODE: TRAUMA-INFORMED EMOTIONAL CHECK-IN
# ─────────────────────────────────────────────
def emotional_checkin_node(state: AgentState) -> AgentState:
    llm = get_llm()
    lang = state.get("language", "en")
    score = state.get("helplessness_score", 5)
    category = state.get("incident_category", "unknown")
    playbooks = load_playbooks()

    matched_note = ""
    for inc in playbooks["incident_types"]:
        if inc["id"] == category:
            key = "emotional_note_sw" if lang == "sw" else "emotional_note_en"
            matched_note = inc.get(key, "")
            break

    if lang == "sw":
        system = (
            "Wewe ni mshauri wa msaada wa kidijitali anayeelewa majeraha ya kisaikolojia. "
            "Unasaidia mtu aliyepitia shambulio la mtandao. Kuwa mwenye huruma, utulivu, na uelewa. "
            "Usimshauri kwenda kwa daktari. Kiswahili tu."
        )
        prompt = (
            f"Mtu alipitia: {category}. Kiwango cha kutokuwa na nguvu: {score}/10.\n"
            f"Kumbuka: \"{matched_note}\"\n\n"
            f"Andika (muundo: [UTHIBITISHO]...[ZOEZI]...[UJUMBE]...):\n"
            f"1. Uthibitisho wa kihisia (sentensi 2-3) kwa kiwango cha {score}/10"
            f"{'. Faraja ya ziada na ukumbushe msaada wa ndani.' if score >= 7 else '.'}\n"
            f"2. Zoezi moja fupi la dakika moja (pumziko AU ardhi AU taarifa ya nguvu)\n"
            f"3. Ujumbe mfupi wa kutia nguvu (sentensi 1-2). Kiswahili tu."
        )
    else:
        system = (
            "You are a trauma-informed digital crisis support specialist for CyberFirstAid AI. "
            "Support people who have just experienced a cyber attack. "
            "Be warm, calm, validating. Never provide medical diagnoses. English only."
        )
        prompt = (
            f"Person experienced: {category}. Helplessness score: {score}/10.\n"
            f"Context: \"{matched_note}\"\n\n"
            f"Write (format: [VALIDATION]...[EXERCISE]...[MESSAGE]...):\n"
            f"1. Emotional validation (2-3 sentences) for score {score}/10"
            f"{'. Extra comfort + mention local support.' if score >= 7 else '.'}\n"
            f"2. One brief 1-minute exercise (breathing OR grounding OR agency statement)\n"
            f"3. Short empowering closing (1-2 sentences). English only."
        )

    try:
        state["emotional_response"] = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ]).content.strip()
    except Exception as e:
        state["emotional_response"] = (
            "Unafanya jambo sahihi. Pumzika — vuta pumzi polepole mara tatu. Umechukua hatua muhimu leo."
            if lang == "sw" else
            "You are doing the right thing. Take a slow breath. You have taken important steps today."
        )
        state["error"] = str(e)

    # Resilience exercise based on score
    if lang == "sw":
        if score <= 3:
            ex = "✨ **Taarifa ya Nguvu:** Sema hivi kwa sauti: *'Nilichukua hatua leo. Ninadhibiti tena maisha yangu ya kidijitali.'*"
        elif score <= 6:
            ex = "🌿 **Zoezi la Ardhi:** Taja vitu **3** unavyoviona, **2** unavyovigusa, **1** unaloisikia. Hii inakurejesha kwenye wakati huu huu."
        else:
            ex = "🌬️ **Pumziko la Kutuliza:** Vuta pumzi kwa sekunde **4**... Shikilia **4**... Toa pumzi kwa **6**. Fanya mara **3**."
    else:
        if score <= 3:
            ex = "✨ **Agency Statement:** Say out loud: *'I took action today. I am reclaiming control of my digital life.'*"
        elif score <= 6:
            ex = "🌿 **Grounding:** Name **3** things you see, **2** you can touch, **1** you hear. This brings you back to the present."
        else:
            ex = "🌬️ **Calming Breath:** Inhale **4** sec... Hold **4**... Exhale **6**. Repeat **3** times."

    state["resilience_exercise"] = ex
    if state.get("confidence_before") is None:
        state["confidence_before"] = score
    return state


# ─────────────────────────────────────────────
# 10. ROUTING
# ─────────────────────────────────────────────
def route_after_classification(state: AgentState) -> str:
    return "technical_recovery" if state.get("incident_category") == "unknown" else "determine_channel"

def route_after_report_assistant(state: AgentState) -> str:
    return "generate_template" if state.get("wants_report", True) else "emotional_checkin"


# ─────────────────────────────────────────────
# 11. BUILD LANGGRAPH
# ─────────────────────────────────────────────
def build_agent():
    wf = StateGraph(AgentState)

    wf.add_node("classify_incident",       classify_incident_node)
    wf.add_node("determine_channel",        determine_reporting_channel_node)
    wf.add_node("technical_recovery",       technical_recovery_node)
    wf.add_node("direct_report_assistant",  direct_report_assistant_node)
    wf.add_node("generate_template",        generate_report_template_node)
    wf.add_node("submission_instructions",  submission_instructions_node)
    wf.add_node("emotional_checkin",        emotional_checkin_node)

    wf.set_entry_point("classify_incident")

    wf.add_conditional_edges("classify_incident", route_after_classification,
        {"determine_channel": "determine_channel", "technical_recovery": "technical_recovery"})
    wf.add_edge("determine_channel",      "technical_recovery")
    wf.add_edge("technical_recovery",     "direct_report_assistant")
    wf.add_conditional_edges("direct_report_assistant", route_after_report_assistant,
        {"generate_template": "generate_template", "emotional_checkin": "emotional_checkin"})
    wf.add_edge("generate_template",      "submission_instructions")
    wf.add_edge("submission_instructions","emotional_checkin")
    wf.add_edge("emotional_checkin",       END)

    return wf.compile()


# ─────────────────────────────────────────────
# 12. PUBLIC RUNNER
# ─────────────────────────────────────────────
def run_agent(
    user_message: str,
    language: str = "en",
    helplessness_score: int = 5,
    wants_report: bool = True,
    conversation_history: list = None,
) -> AgentState:
    agent = build_agent()
    return agent.invoke({
        "user_message": user_message,
        "language": language,
        "conversation_history": conversation_history or [],
        "incident_category": None,
        "incident_severity": None,
        "classification_reasoning": None,
        "recommended_channels": None,
        "chosen_channel": None,
        "wants_report": wants_report,
        "technical_steps": None,
        "technical_summary": None,
        "tzcert_fields": None,
        "report_template": None,
        "submission_instructions": None,
        "helplessness_score": helplessness_score,
        "emotional_response": None,
        "resilience_exercise": None,
        "confidence_before": helplessness_score,
        "confidence_after": None,
        "next_node": None,
        "final_output": None,
        "error": None,
    })
