import logging
import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import VECTOR_DB_DIR, EMBEDDING_MODEL, OLLAMA_HOST

# Setup professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the knowledge directory
KNOWLEDGE_DIR = Path(__file__).parent.parent / "data" / "knowledge"

def build_knowledge_base():
    """Scans the knowledge folder for PDFs and ingests them into ChromaDB."""
    
    if not KNOWLEDGE_DIR.exists():
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Knowledge directory created at {KNOWLEDGE_DIR}. Please drop your PDFs there.")
        return

    logger.info(f"🚀 Starting RAG Ingestion from: {KNOWLEDGE_DIR}")

    # 1. Load all PDFs from the directory using DirectoryLoader for efficiency
    loader = DirectoryLoader(
        str(KNOWLEDGE_DIR), 
        glob="**/[!.]*.*", 
        loader_cls=PyPDFLoader, # type: ignore
        show_progress=True
    )
    
    try:
        raw_documents = loader.load()
        if not raw_documents:
            logger.error("No PDF documents found in data/knowledge/. Ingestion aborted.")
            return
        logger.info(f"Successfully loaded {len(raw_documents)} pages from PDF reports.")
    except Exception as e:
        logger.error(f"Failed to load PDFs: {e}")
        return

    # 2. Optimized Chunking for DeepSeek-R1
    # We use a larger chunk size because the 32B model has a 32k context window.
    # This allows the AI to see more 'surrounding context' for each finding.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=250,
        add_start_index=True
    )
    docs = text_splitter.split_documents(raw_documents)
    logger.info(f"Split reports into {len(docs)} high-context chunks.")

    # 3. Embedding Engine
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_HOST
    )

    # 4. Create & Persist Vector Store
    try:
        # Clear old database to prevent duplicate entries if re-running
        if VECTOR_DB_DIR.exists():
            import shutil
            shutil.rmtree(VECTOR_DB_DIR)
            
        vector_db = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=str(VECTOR_DB_DIR)
        )
        logger.info(f"✅ SUCCESS: {len(docs)} chunks vaulted in {VECTOR_DB_DIR}")
    except Exception as e:
        logger.error(f"Knowledge Ingestion Failed: {e}")

if __name__ == "__main__":
    build_knowledge_base()