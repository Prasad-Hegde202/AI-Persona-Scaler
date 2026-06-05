from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

pdf_path = "data/resume.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text()

# Clean spacing
text = re.sub(r'(?<=\w)\s(?=\w)', '', text)

# Chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_text(text)

print(f"\nTotal Chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks):
    print("=" * 50)
    print(f"CHUNK {i+1}")
    print("=" * 50)
    print(chunk[:500])
    print("\n")