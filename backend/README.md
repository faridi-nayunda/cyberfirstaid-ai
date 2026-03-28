# 🛡️ CyberFirstAid AI
**iSAFE Hackathon 2026 — Challenge 2: Defend the Digital Citizen**

> Immediate agentic help after a cyber attack — For Tanzania | Msaada wa haraka wa kiagentic baada ya shambulio la mtandao — Kwa Tanzania

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Groq API Key
Get a free key at https://console.groq.com

Option A — via UI (sidebar input)
Option B — via .env file:
```
GROQ_API_KEY=your_key_here
```

### 3. Run the app
```bash
streamlit run app.py
```

---

## 🏗️ Architecture (LangGraph Flow)

```
User Message
    ↓
[Node 1] Classify Incident
    ↓
[Node 2] Determine Best Reporting Channel
    ↓
[Node 3] Technical Recovery Steps
    ↓
[Node 4] Direct Report Assistant
    ↓ (if wants_report=True)
[Node 5] Generate Tailored Report Template
    ↓
[Node 6] Copy-Paste + Submission Instructions
    ↓
[Node 7] Trauma-Informed Emotional Check-in
    ↓
END
```

## 📁 Project Structure
```
cyberfirstaid/
├── app.py                  # Streamlit UI
├── requirements.txt
├── agent/
│   └── graph.py            # LangGraph agent (all nodes)
└── data/
    └── playbooks.json      # Tanzania-specific incident knowledge base
```

## 🌍 WSIS & SDG Alignment
- **WSIS C5** — Building confidence and security in ICTs
- **WSIS C4** — Capacity building
- **WSIS C10** — Ethical dimensions of AI
- **SDG 16** — Peace, justice, strong institutions
- **SDG 4** — Quality education / digital resilience
- **SDG 9** — Innovation and infrastructure
- **SDG 10** — Reduced inequalities (Global South focus)

## 🔧 Tech Stack
- **LangGraph** — Agentic stateful workflow
- **LangChain + Groq** — LLM (llama-3.1-8b-instant)
- **Streamlit** — UI
- **ChromaDB** — Vector database (available for extension)
- **Swahili + English** — Full bilingual support
