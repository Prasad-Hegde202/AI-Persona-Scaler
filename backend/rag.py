import os
from dotenv import load_dotenv

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from langchain_chroma import Chroma

from google import genai

# ---------------------------
# Load Environment Variables
# ---------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# ---------------------------
# Gemini Client
# ---------------------------

client = genai.Client(
    api_key=api_key
)

# ---------------------------
# Embedding Model
# ---------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

# ---------------------------
# Load ChromaDB
# ---------------------------

vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# ---------------------------
# User Question
# ---------------------------

question = input("\nAsk a Question: ")

# ---------------------------
# Retrieve Relevant Chunks
# ---------------------------

results = vector_store.similarity_search_with_relevance_scores(
    question,
    k=8
)

filtered_docs = []

for doc, score in results:

    # Adjust threshold if needed
    if score >= 0.4:
        filtered_docs.append(doc)

# ---------------------------
# Build Context
# ---------------------------

context = "\n\n".join(
    [doc.page_content for doc in filtered_docs]
)

# ---------------------------
# Prompt
# ---------------------------

prompt = f"""
You are Prasad Hegde's AI representative.

Rules:

1. Answer ONLY from the provided context.

2. Never make up information.

3. Never assume facts.

4. If the answer is not available in the context,
reply EXACTLY:

I don't have enough information to answer that.

5. Stay in character as Prasad's AI representative.

Context:
{context}

Question:
{question}
"""

# ---------------------------
# Generate Answer
# ---------------------------

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=prompt
)

# ---------------------------
# Output
# ---------------------------

print("\n===== ANSWER =====\n")

print(response.text)