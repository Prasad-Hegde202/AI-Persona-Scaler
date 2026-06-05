import os
import re
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_chroma import Chroma

# ---------------------------
# Load API Key
# ---------------------------
load_dotenv()

# ---------------------------
# Read Resume
# ---------------------------
pdf_path = "data/resume.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text()

# Clean spacing
text = re.sub(r'(?<=\w)\s(?=\w)', '', text)

# ---------------------------
# Create Chunks
# ---------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_text(text)

print(f"\nTotal Chunks: {len(chunks)}")

# ---------------------------
# Gemini Embeddings
# ---------------------------
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# ---------------------------
# Store in ChromaDB
# ---------------------------
vector_store = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"
)

print("\nResume stored successfully in ChromaDB!")