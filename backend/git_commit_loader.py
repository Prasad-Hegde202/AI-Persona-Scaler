import os
from dotenv import load_dotenv
from github import Github

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
# Existing ChromaDB
# =====================================

vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# =====================================
# Process Commits
# =====================================

print("\n===== COMMIT INGESTION STARTED =====\n")

total_commits = 0

for repo in repos:

    print(f"\nProcessing Repo: {repo.name}")

    try:

        commits = repo.get_commits()

        commit_texts = []
        metadatas = []

        # Last 20 commits per repo
        for commit in commits[:20]:

            message = commit.commit.message

            commit_text = f"""
Repository: {repo.name}

Commit Message:
{message}
"""

            commit_texts.append(commit_text)

            metadatas.append({
                "source": "github",
                "repo": repo.name,
                "type": "commit"
            })

        if commit_texts:

            vector_store.add_texts(
                texts=commit_texts,
                metadatas=metadatas
            )

            total_commits += len(commit_texts)

            print(
                f"Stored {len(commit_texts)} commits"
            )

    except Exception as e:

        print(
            f"Skipping {repo.name}: {str(e)}"
        )

print("\n================================")
print("COMMIT INGESTION COMPLETED")
print(f"Total Commits Stored: {total_commits}")
print("================================")