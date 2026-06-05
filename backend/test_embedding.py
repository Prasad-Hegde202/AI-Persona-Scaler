import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector = embeddings.embed_query(
    "Tell me about NextStep AI"
)

print(f"Vector Length: {len(vector)}")
print(vector[:10])