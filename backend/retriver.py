import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# -----------------------
# Load API Key
# -----------------------
load_dotenv()

# -----------------------
# Embedding Model
# -----------------------
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------
# Load Existing ChromaDB
# -----------------------
vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# -----------------------
# User Question
# -----------------------
question = "What recent changes were made in Auto-Trader? "

# -----------------------
# Search Similar Chunks
# -----------------------
results = vector_store.similarity_search(
    question,
    k=3
)

print("\n===== RETRIEVED CHUNKS =====\n")

for i, doc in enumerate(results):
    print("=" * 50)
    print(f"RESULT {i+1}")
    print("=" * 50)
    print("Metadata:")
    print(doc.metadata)
    print("\nContent:")
    print(doc.page_content)
    print("\n")