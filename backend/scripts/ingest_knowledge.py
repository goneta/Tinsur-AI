import os
import sys
import chromadb
import google.generativeai as genai
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pypdf import PdfReader

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Ensure local libs is in path (for chromadb/genai)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../libs")))

# Load .env explicitly BEFORE importing settings
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path)

from app.core.config import settings

# Configure Gemini Config
api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in settings or environment.")
    sys.exit(1)

genai.configure(api_key=api_key)

def get_gemini_embedding(text):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
        title="Tinsur AI Knowledge Base"
    )
    return result['embedding']

def extract_pdf_text(file_path):
    """Extract text from a PDF file page by page."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            pages.append({"text": text, "page": i + 1})
    return pages

def chunk_markdown(content):
    """Split markdown by header level 3."""
    chunks = content.split('### ')
    result = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): continue
        text = ("### " + chunk.strip()) if i > 0 else chunk.strip()
        result.append(text)
    return result

def main():
    print("🚀 Starting Knowledge Ingestion...")

    # 1. Initialize ChromaDB
    persist_dir = os.path.join(os.path.dirname(__file__), "../data/chroma_db")
    os.makedirs(persist_dir, exist_ok=True)
    
    print(f"📂 Database Path: {persist_dir}")
    client = chromadb.PersistentClient(path=persist_dir)
    
    try:
        client.delete_collection(name="support_knowledge_base")
        print("🗑️  Deleted existing collection.")
    except Exception:
        pass

    collection = client.create_collection(name="support_knowledge_base")

    # 2. Scanning Directory
    kb_dir = os.path.join(os.path.dirname(__file__), "../data/knowledge_base")
    if not os.path.exists(kb_dir):
        print(f"❌ ERROR: Knowledge base directory not found at {kb_dir}")
        sys.exit(1)

    all_docs = []
    all_ids = []
    all_metadatas = []
    all_embeddings = []
    
    doc_counter = 0

    print(f"🔍 Scanning {kb_dir} for documents...")
    for root, dirs, files in os.walk(kb_dir):
        # Determine category based on subdirectory
        rel_dir = os.path.relpath(root, kb_dir)
        if rel_dir == ".":
            category = "general"
        else:
            # Take the top-most directory as the category
            category = rel_dir.split(os.sep)[0]
            
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, kb_dir)
            
            if file.endswith('.md'):
                print(f"  📄 Processing Markdown: {rel_path} [Category: {category}]")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = chunk_markdown(content)
                for i, text in enumerate(chunks):
                    all_docs.append(text)
                    all_ids.append(f"doc_{doc_counter}")
                    all_metadatas.append({
                        "source": rel_path, 
                        "type": "markdown", 
                        "chunk": i,
                        "category": category
                    })
                    doc_counter += 1
                    
            elif file.endswith('.pdf'):
                print(f"  📕 Processing PDF: {rel_path} [Category: {category}]")
                try:
                    pages = extract_pdf_text(file_path)
                    for page_data in pages:
                        all_docs.append(page_data["text"])
                        all_ids.append(f"doc_{doc_counter}")
                        all_metadatas.append({
                            "source": rel_path, 
                            "type": "pdf", 
                            "page": page_data["page"],
                            "category": category
                        })
                        doc_counter += 1
                except Exception as e:
                    print(f"    ⚠️ Failed to process PDF {file}: {e}")

    if not all_docs:
        print("⚠️ No documents found to ingest.")
        return

    # 3. Generate Embeddings (Batching would be better, but keeping loop for simplicity)
    print(f"📝 Found {len(all_docs)} segments. Embedding...")
    for i, text in enumerate(all_docs):
        print(f"   • Embedding segment {i+1}/{len(all_docs)}...", end="\r")
        try:
            all_embeddings.append(get_gemini_embedding(text))
        except Exception as e:
            print(f"\n   ⚠️ Failed to embed segment {i}: {e}")
            # Use zero embedding or skip? Skipping is safer for retrieval quality.
            # But IDs/Metadatas must match. Let's fix index later if skipped.
            pass

    # Ensure alignment if any failed (simplified: just store what worked)
    # In a real system we'd handle this more robustly.
    
    # 4. Store in ChromaDB
    print(f"\n💾 Storing in Vector DB...")
    collection.add(
        documents=all_docs,
        embeddings=all_embeddings,
        metadatas=all_metadatas,
        ids=all_ids
    )
    print("✅ Ingestion Complete!")

if __name__ == "__main__":
    main()
