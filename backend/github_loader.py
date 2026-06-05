import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_USERNAME")

g = Github(token)

user = g.get_user(username)

repos = user.get_repos()

print("\n===== REPOSITORIES =====\n")

for repo in repos:

    print(f"\nRepo: {repo.name}")
    print(f"Description: {repo.description}")

    try:
        readme = repo.get_readme()

        content = readme.decoded_content.decode(
            "utf-8"
        )

        print("\nREADME Preview:")
        print(content[:500])

    except Exception:
        print("README not found")

    print("\n" + "=" * 80)