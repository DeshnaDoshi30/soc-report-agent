import logging
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from src.config import VECTOR_DB_DIR, EMBEDDING_MODEL, OLLAMA_HOST

# Setup professional logging
logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self):
        """Initializes the connection to the local Vector Vault."""
        try:
            # 1. Setup the Embedding Engine (Must match ingestion)
            self.embeddings = OllamaEmbeddings(
                model=EMBEDDING_MODEL,
                base_url=OLLAMA_HOST
            )

            # 2. Load the Existing ChromaDB
            # This points to the data/vector_db/ folder we created earlier
            self.vector_db = Chroma(
                persist_directory=str(VECTOR_DB_DIR),
                embedding_function=self.embeddings
            )
            logger.info("Forensic Knowledge Base successfully connected.")
            
        except Exception as e:
            logger.error(f"Failed to connect to Knowledge Base: {e}")
            self.vector_db = None

    def get_context(self, query: str, k: int = 3) -> str:
        """
        Retrieves the top 'k' most relevant past incidents or 
        hardening guides based on the semantic query.
        """
        if not self.vector_db:
            return "No historical context available."

        try:
            # Perform Semantic Search
            # This finds reports based on 'meaning', not just keywords
            results = self.vector_db.similarity_search(query, k=k)
            
            # Format results into a single block of text for the LLM
            context_block = "\n---\n".join([doc.page_content for doc in results])
            
            logger.info(f"Retrieved {len(results)} relevant historical documents.")
            return context_block

        except Exception as e:
            logger.error(f"Knowledge Retrieval Failed: {e}")
            return "Error retrieving historical context."

# Helper function for easy integration into the main pipeline
def fetch_expert_context(query: str) -> str:
    kb = KnowledgeBase()
    return kb.get_context(query)