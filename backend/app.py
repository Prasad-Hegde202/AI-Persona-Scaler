import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from google import genai

import requests

from datetime import (
    datetime,
    timedelta,
    timezone
)


# =====================================
# Load Environment Variables
# =====================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CAL_API_KEY = os.getenv("CAL_API_KEY")

CAL_EVENT_TYPE_ID = int(
    os.getenv("CAL_EVENT_TYPE_ID", "5914537")
)

# =====================================
# Gemini Client
# =====================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# =====================================
# Calendar Link
# =====================================

CALENDAR_LINK = (
    "https://cal.com/prasad-hegde-juxhoa/scaler-ai-interview"
)

# =====================================
# Embedding Model
# =====================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY
)

# =====================================
# Load ChromaDB
# =====================================

vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# =====================================
# Flask App
# =====================================

app = Flask(__name__)

CORS(app)

# =====================================
# Health Check
# =====================================

@app.route("/")
def home():

    return jsonify(
        {
            "status": "running",
            "message": "AI Persona Backend Active"
        }
    )

# =====================================
# Chat Endpoint
# =====================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        question = data.get(
            "question",
            ""
        ).strip()

        # =====================================
        # Empty Question Check
        # =====================================

        if not question:

            return jsonify(
                {
                    "answer": "Please enter a question.",
                    "sources": []
                }
            )

        question_lower = question.lower()

        # =====================================
        # Booking Keywords
        # =====================================

        booking_keywords = [
            "schedule",
            "interview",
            "meeting",
            "book",
            "availability"
        ]

        # =====================================
        # Booking Intent Detection
        # =====================================

        if any(
            keyword in question_lower
            for keyword in booking_keywords
        ):

            return jsonify(
                {
                    "answer": f"""Absolutely.

You can schedule an interview using my live calendar:

{CALENDAR_LINK}

My availability is synced with my real calendar.""",
                    "sources": [
                        {
                            "repo": "cal.com",
                            "type": "calendar"
                        }
                    ]
                }
            )

        # =====================================
        # Retrieve Relevant Chunks
        # =====================================

        results = vector_store.similarity_search_with_relevance_scores(
            question,
            k=8
        )

        filtered_docs = []

        for doc, score in results:

            print(
                f"Score: {round(score, 4)}"
            )

            if score >= 0.4:
                filtered_docs.append(doc)

        # =====================================
        # No Relevant Context Found
        # =====================================

        if len(filtered_docs) == 0:

            return jsonify(
                {
                    "answer":
                    "I don't have enough information to answer that.",
                    "sources": []
                }
            )

        # =====================================
        # Build Context
        # =====================================

        context = "\n\n".join(
            [
                doc.page_content
                for doc in filtered_docs
            ]
        )

        # =====================================
        # Collect Unique Sources
        # =====================================

        unique_sources = []

        seen = set()

        for doc in filtered_docs:

            repo = doc.metadata.get(
                "repo",
                "resume"
            )

            source_type = doc.metadata.get(
                "type",
                "resume"
            )

            source_key = (
                f"{repo}-{source_type}"
            )

            if source_key not in seen:

                seen.add(source_key)

                unique_sources.append(
                    {
                        "repo": repo,
                        "type": source_type
                    }
                )

        # =====================================
        # Prompt
        # =====================================

        prompt = f"""
You are Prasad Hegde's AI representative.

Rules:

1. Answer ONLY using the provided context.

2. Never make up information.

3. Never assume facts.

4. If the answer is not available in the context,
reply exactly:

I don't have enough information to answer that.

5. Keep answers professional and concise.

6. Stay in character as Prasad's AI representative.

Context:
{context}

Question:
{question}
"""

        # =====================================
        # Generate Answer
        # =====================================

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        answer = response.text

        # =====================================
        # Return Response
        # =====================================

        return jsonify(
            {
                "answer": answer,
                "sources": unique_sources
            }
        )

    # ✅ FIX 1: except now correctly aligned with try
    except Exception as e:

        print("ERROR:", str(e))

        return jsonify(
            {
                "answer":
                "I'm currently unable to access my knowledge base. Please try again in a few moments.",
                "sources": []
            }
        ), 500

@app.route(
    "/check-availability",
    methods=["GET"]
)
def check_availability():

    try:

        headers = {
            "Authorization":
            f"Bearer {CAL_API_KEY}"
        }

        start_time = datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        end_time = (
            start_time +
            timedelta(days=7)
        ).replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=0
        )

        url = (
            "https://api.cal.com/v2/slots/available"
            f"?eventTypeId={CAL_EVENT_TYPE_ID}"
            f"&startTime={start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
            f"&endTime={end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        print("\n========== CAL DEBUG ==========")
        print("URL:", url)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("================================\n")

        print("URL:", url)

        data = response.json()

        print("PARSED DATA:", data)

        slots = []

        for day_slots in data.get(
            "data",
            {}
        ).get(
            "slots",
            {}
        ).values():

            for slot in day_slots:

                slots.append(
                    slot["time"]
                )

        return jsonify({
            "available_slots":
            slots[:10]
        })

    except Exception as e:

        print(
            "CALENDAR ERROR:",
            str(e)
        )

        return jsonify({
            "available_slots": []
        }), 500

@app.route(
    "/book-interview",
    methods=["POST"]
)
def book_interview():

    try:

        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        slot = data.get("slot")

        headers = {
            "Authorization":
            f"Bearer {CAL_API_KEY}",
            "Content-Type":
            "application/json"
        }

        payload = {
    "eventTypeId": CAL_EVENT_TYPE_ID,

    "start": slot,

    "responses": {
        "name": name,
        "email": email,
        "location": {
            "value": "integrations:daily",
            "optionValue": ""
        }
    },

    "timeZone": "Asia/Kolkata",

    "language": "en",

    "metadata": {}
}

        response = requests.post(
            "https://api.cal.com/v2/bookings",
            headers=headers,
            json=payload,
            timeout=20
        )

        print(response.status_code)
        print(response.text)
        

        booking_data = response.json()

        return jsonify({
             "success": response.status_code in [200, 201],
            "booking": booking_data
        })

        
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

    except Exception as e:

        print(
            "BOOKING ERROR:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route(
    "/voice-chat",
    methods=["POST"]
)
def voice_chat():

    try:

        data = request.get_json()

        question = data.get(
            "question",
            ""
        ).strip()

        if not question:

            return jsonify({
                "answer":
                "Please provide a question."
            })

        results = (
            vector_store
            .similarity_search_with_relevance_scores(
                question,
                k=8
            )
        )

        # ✅ FIX 2: filtered_docs correctly indented (removed extra spaces)
        filtered_docs = []

        for doc, score in results:

            if score >= 0.4:

                filtered_docs.append(doc)

        # ✅ FIX 3 & 4: Only ONE no-context check, duplicate block removed entirely
        if len(filtered_docs) == 0:

            return jsonify({
                "answer":
                "I don't have enough information to answer that."
            })

        context = "\n\n".join(
            [
                doc.page_content
                for doc in filtered_docs
            ]
        )

        prompt = f"""
You are Prasad Hegde's AI representative.

Rules:

1. Answer only from the context.

2. Keep answers short and conversational.

3. These answers will be spoken on a phone call.

4. Never invent information.

5. If information is unavailable say:

'I don't have enough information to answer that.'

Context:
{context}

Question:
{question}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        return jsonify({
            "answer":
            response.text
        })

    except Exception:

        return jsonify({
            "answer":
            "I'm currently unable to access my knowledge base. Please try again in a moment."
        })

# =====================================
# Run Server
# =====================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
