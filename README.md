#  Prasad AI Persona

An AI-powered voice and chat assistant that represents me professionally, answers questions about my background, projects, education, and technical skills, and can automatically schedule interviews using my real calendar.

Built as part of an AI Persona assignment combining Voice AI, Retrieval-Augmented Generation (RAG), and real-time interview scheduling.

---

##  Features

###  AI Chat Assistant

* Answers questions about my education, skills, projects, and experience.
* Uses Retrieval-Augmented Generation (RAG) instead of hardcoded responses.
* Grounded on my resume, GitHub repositories, and project documentation.

###  AI Voice Agent

* Supports natural voice conversations through Vapi.
* Handles follow-up questions and interruptions.
* Provides recruiter-friendly responses about my profile.

###  RAG Knowledge Base

* Resume data
* GitHub project repositories
* Project documentation
* ChromaDB vector database
* Gemini Embeddings

###  Automated Interview Scheduling

* Checks real-time availability using Cal.com.
* Books confirmed interview slots automatically.
* Creates calendar events and meeting links without human intervention.

---

##  System Architecture

###  Chat Flow

```text
User
  │
  ▼
React Chat Interface                                          
  │
  ▼
Flask Backend (/chat)
  │
  ├─────────────► ChromaDB
  │                 │
  │                 ▼
  │        Resume + GitHub + Projects
  │
  ▼
Gemini 2.5 Flash Lite
  │
  ▼
Chat Response
```

###  Voice Agent Flow

```text
Caller
  │
  ▼
Vapi Voice Agent
  │
  ▼
Flask Backend (/voice-chat)
  │
  ├─────────────► ChromaDB
  │                 │
  │                 ▼
  │        Resume + GitHub + Projects
  │
  ▼
Gemini 2.5 Flash Lite
  │
  ▼
Voice Response
```

###  Interview Scheduling Flow

```text
Caller / Recruiter
        │
        ▼
   Vapi Voice Agent
        │
        ▼
 Flask Backend
        │
        ├────────────► /check-availability
        │                    │
        │                    ▼
        │               Cal.com API
        │
        └────────────► /book-interview
                             │
                             ▼
                        Cal.com API
                             │
                             ▼
                      Google Calendar
                             │
                             ▼
                 Confirmed Interview Slot
```

---

##  Tech Stack

### Frontend

* React.js
* Axios

### Backend

* Flask
* Python

### AI & RAG

* Google Gemini 2.5 Flash Lite
* Gemini Embeddings
* LangChain
* ChromaDB

### Voice AI

* Vapi

### Scheduling

* Cal.com
* Google Calendar

### Deployment

* Render
* Vercel

---

##  Project Structure

```text
AI-Persona/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app.py
│   ├── chroma_db/
│   ├── requirements.txt
│   └── .env
│
└── README.md
```

---

##  Environment Variables

Create a `.env` file inside the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key
CAL_API_KEY=your_cal_api_key
CAL_EVENT_TYPE_ID=your_event_type_id
```

---


---

##  Evaluation Summary

| Metric                 | Result |
| ---------------------- | ------ |
| First Response Latency | ~1.6s  |
| Transcription Accuracy | ~90%   |
| Booking Success Rate   | ~90%   |
| Hallucination Rate     | ~5%    |
| Retrieval Precision    | ~90%   |
| Retrieval Recall       | ~88%   |

---

##  Cost Breakdown

### Chat Session

* Gemini Flash Lite API usage
* Approximate cost: very low (< $0.01 per short conversation)

### Voice Calls

* Vapi voice processing
* Telephony charges based on call duration

### Infrastructure

* Render (Backend)
* Vercel (Frontend)

---

##  Future Improvements

* Add LinkedIn and certification data to the knowledge base.
* Add conversation memory for more natural voice interactions.
* Build automated evaluation dashboards for monitoring system quality.

---

##  Author

**Prasad Hegde**

MSc Computer Science & Information Technology
JAIN University, Bangalore

AI Persona | RAG Systems | Machine Learning | Full Stack Development
