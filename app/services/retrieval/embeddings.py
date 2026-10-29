import time
import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings


# ── Variables ───────────────────────────────────────────────────────
BATCH_SIZE = 50
_GEMINI_DEM = 3072
_FALLBACK_DIM = 768     # all-mpnet-base-v2

_active_model = None
_model_type: str | None = None  # "gemini" or "fallback"


# ── Model initialisation ───────────────────────────────────────────────────────


