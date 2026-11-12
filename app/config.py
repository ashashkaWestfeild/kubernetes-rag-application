import os
from dotenv import load_dotenv  


load_dotenv()

class Settings:
    # --- GEMINI EMBEDDINGS ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # --- VECTOR DB (QDRANT) ---
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = "enterprise_rag"
    
    # --- REASONING ENGINE (GROQ) ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # GROQ_MODEL = "llama-3.3-70b-versatile"
    GROQ_MODEL = "qwen/qwen3.8-27b"
    GROQ_FALLBACK_API_KEY = os.getenv("GROQ_FALLBACK_API_KEY")

    # --- LLM GATEWAY (LiteLLM proxy) ---
    LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "http://localhost:4000/v1")
    LLM_GATEWAY_KEY = os.getenv("LITELLM_MASTER_KEY")

settings = Settings()
