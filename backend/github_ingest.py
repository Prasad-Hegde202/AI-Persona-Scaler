import os
from dotenv import load_dotenv
from github import Github

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# =====================================
# Load Environment Variables
# =====================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =====================================
# GitHub Connection
# =====================================

github = Github(GITHUB_TOKEN)

user = github.get_user(GITHUB_USERNAME)

repos = user.get_repos()

# =====================================
# Gemini Embeddings
# =====================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY
)

# =====================================
# Connect Existing ChromaDB
# =====================================

vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# =====================================
# Text Splitter
# =====================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

print("\n===== GITHUB INGESTION STARTED =====\n")

total_chunks = 0

# =====================================
# Process Repositories
# =====================================

for repo in repos:

    print(f"\nProcessing Repo: {repo.name}")

    try:

        readme = repo.get_readme()

        content = readme.decoded_content.decode(
            "utf-8",
            errors="ignore"
        )

        if not content.strip():
            print("Empty README")
            continue

        chunks = splitter.split_text(content)

        metadatas = []

        for _ in chunks:

            metadatas.append({
                "source": "github",
                "repo": repo.name,
                "type": "readme"
            })

        vector_store.add_texts(
            texts=chunks,
            metadatas=metadatas
        )

        total_chunks += len(chunks)

        print(
            f"Stored {len(chunks)} chunks"
        )

    except Exception as e:

        print(
            f"Skipping {repo.name}: {str(e)}"
        )

print("\n================================")
print("GITHUB INGESTION COMPLETED")
print(f"Total Chunks Stored: {total_chunks}")
print("================================")