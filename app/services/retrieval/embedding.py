import time
import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings


# ── Variables ───────────────────────────────────────────────────────
BATCH_SIZE = 50
_GEMINI_DIM = 3072
_FALLBACK_DIM = 768     # all-mpnet-base-v2

_active_model = None
_model_type: str | None = None  # "gemini" or "fallback"


# ── Model initialisation ───────────────────────────────────────────────────────

def _probe_gemini():
    """Try one embed call to verify Gemini is reachable. Returns model or None.
       Checking if out main embed model is active"""
    try:
        model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2-preview",
            google_api_key=settings.GEMINI_API_KEY,
        )
        model.embed_query("probe")
        logfire.info("Gemini embeddings ready (gemini-embedding-2-preview, 3072-dim).")
        return model
    except Exception as e:
        logfire.warning(f"Gemini probe failed: {e}. Will use sentence-transformers fallback.")
    return None

def _load_fallback():
    """If our main embed model is not active then we use the fallback model"""
    from sentence_transformers import SentenceTransformer
    logfire.info("Loading sentence-transformers fallback (all-mpnet-base-v2, 768-dim).")
    return SentenceTransformer("all-mpnet-base-v2")

def _init():
    """Initialise embedding model once per process. Called lazily on first use."""
    global _active_model, _model_type   # defining global variables 
    if _active_model is not None: # Check if there any model is active 
        return

    """If main gemini is active then use this if not use fallback model as active model"""
    gemini = _probe_gemini()
    if gemini:
        _active_model = gemini
        _model_type = "gemini"
    else:
        _active_model = _load_fallback()
        _model_type = "fallback"

# ── Public helpers ─────────────────────────────────────────────────────────────

def get_embedding_dim() -> int:
    """Return the vector dimension for the active model. Call after _init()."""
    _init()
    return _GEMINI_DIM if _model_type == "gemini" else _FALLBACK_DIM


# ── Batch embedding with retry ─────────────────────────────────────────────────

def _embed_batch(batch: list[str]) -> list[list[float]]:
    """Embed one batch of texts. Gemini retries rate-limit errors with exponential backoff (1 s, 2 s, 4 s); the local fallback model never retries."""
    if _model_type == "gemini":
        # Exponential backoff: 4 attempts, waiting 1 s -> 2 s -> 4 s between them
        for attempt in range(4):
            try:
                # One API call for the whole batch (saves RPM/RPD quota)
                return _active_model.embed_documents(batch)
            except Exception as e:
                err = str(e).lower()
                # Retry only transient quota errors; anything else (bad key, bad input) fails immediately
                is_rate_limit = any(x in err for x in ("429", "rate", "quota", "resource_exhausted"))
                if is_rate_limit and attempt < 3:
                    wait = 2 ** attempt  # 1, 2, 4 seconds
                    logfire.warning(
                        f"Gemini rate limit hit — retrying in {wait}s "
                        f"(attempt {attempt + 1}/4)."
                    )
                    time.sleep(wait)
                else:
                    # Non-rate-limit error, or retries used up: log and re-raise the original error
                    logfire.error(f"Gemini embedding failed: {e}")
                    raise
        # Safety net only: every path above returns or raises, so this line is never reached
        raise RuntimeError("Gemini rate limit persisted after 4 attempts.")
    else:
        # Fallback: local sentence-transformers model, no API, no rate limit; numpy array -> plain lists
        return _active_model.encode(batch, show_progress_bar=False).tolist()

# ── Public API (same signatures as before) ─────────────────────────────────────

def embed_query(query: str) -> list[float]:
    """Embed a single user question at query time, with the same model that embedded the chunks."""
    _init()  # lazy-load the model on first use
    if _model_type == "gemini":
        # Query-specific call (RETRIEVAL_QUERY task type), not embed_documents
        # NOTE: bypasses _embed_batch, so there is no 429 retry at query time
        return _active_model.embed_query(query)
    # encode() expects a list; take the single vector back out
    return _active_model.encode([query])[0].tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed many chunks at ingestion time in batches of BATCH_SIZE, logging one Logfire span per batch."""
    _init()  # lazy-load the model on first use
    all_embeddings: list[list[float]] = []
    # Walk the chunks in BATCH_SIZE steps; output order matches input order
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        # One span per batch: shows which batch was slow or failed, and where to resume
        with logfire.span("Embed batch", model=_model_type, start=i, size=len(batch)):
            all_embeddings.extend(_embed_batch(batch))
    return all_embeddings




