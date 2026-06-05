import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from google import genai

# =====================================
# Load Environment Variables
# =====================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify(
            {
                "error": str(e)
            }
        ), 500

# =====================================
# Run Server
# =====================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )