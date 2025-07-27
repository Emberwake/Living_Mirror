# Reconstructed v1.3 API
from fastapi import FastAPI
app = FastAPI()


from fastapi import Body
from pydantic import BaseModel
import json

class FeedbackInput(BaseModel):
    session_id: str
    module_triggered: str
    tone_detected: str
    notes: Optional[str] = None

FEEDBACK_LOG_PATH = "mirror_log.jsonl"

def write_feedback_log(data: dict):
    try:
        with open(FEEDBACK_LOG_PATH, "a", encoding="utf-8") as f:
            json.dump(data, f)
            f.write("\n")
    except Exception as e:
        print("Log write error:", e)

@app.post("/mirror/feedback")
async def feedback_endpoint(input: FeedbackInput = Body(...)):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": input.session_id[:12],
        "module_triggered": input.module_triggered,
        "tone_detected": input.tone_detected,
        "notes": input.notes or ""
    }
    write_feedback_log(log_entry)
    return {"status": "received", "entry": log_entry}


from fastapi import Request, HTTPException, Header
from collections import defaultdict, deque
from typing import Optional
import uuid

class MirrorInput(BaseModel):
    message: str

SESSION_HISTORY_LIMIT = 5
MAX_MESSAGE_LENGTH = 600
SESSIONLESS_MODE = False

# In-memory session + lock structure
session_buffers = defaultdict(lambda: deque(maxlen=SESSION_HISTORY_LIMIT))
session_locks = defaultdict(lambda: asyncio.Lock())

@app.post("/mirror/respond")
async def mirror_response(request: Request, input: MirrorInput, x_session_id: Optional[str] = Header(None)):
    text = input.message.strip().lower()

    if not text or len(text) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=422, detail="Message must be non-empty and under length limit.")

    session_id = x_session_id or str(uuid.uuid4())

    async with session_locks[session_id]:
        buffer = session_buffers[session_id]
        buffer.append("default")  # placeholder logic

    return {
        "session_id": session_id,
        "tone_detected": "stable",
        "responses": [{
            "module": "default",
            "response": "This is a placeholder response while reflection logic is restored."
        }]
    }


import unicodedata
import re

def normalize_input(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip().lower())

def safety_filter(text: str) -> bool:
    patterns = [
        r"\bf[*@!#%]+ck\b", r"\bn[i1!]+gg?[ae]r\b", r"\bc[*@!#%]*nt\b", r"\bsu[i1]+c[i1]de\b",
        r"\bkill\s?yourself\b", r"\brape\b", r"\bdie\s?bitch\b", r"[🖕💀🔫]"
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


# --- Shared Semantic Transformer Loader ---

_transformer_model = None

def get_transformer():
    global _transformer_model
    if _transformer_model is None:
        from sentence_transformers import SentenceTransformer
        _transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _transformer_model


from datetime import datetime

def encode_and_match_semantic(text: str):
    model = get_transformer()
    input_embedding = model.encode(text, convert_to_tensor=True)
    matches = []
    for mod, data in modules_config.items():
        phrases = data.get("intent_phrases", [])
        if not phrases:
            continue
        mod_embeddings = model.encode(phrases, convert_to_tensor=True)
        max_score = float(util.cos_sim(input_embedding, mod_embeddings).max())
        if max_score >= data.get("threshold", EMBEDDING_THRESHOLD):
            matches.append((mod, max_score))
    if matches:
        return sorted(matches, key=lambda x: x[1], reverse=True)[0][0]
    return None


def log_module_and_tone(session_id: str, module: str, tone: str):
    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id[:12],
            "matched_module": module,
            "tone_detected": tone
        }
        with open("mirror_log.jsonl", "a", encoding="utf-8") as f:
            json.dump(log_entry, f)
            f.write("\n")
    except Exception as e:
        print("Log error:", e)


async def get_responses_from_input(text: str, session_id: str) -> List[Dict]:
    responses = []
    triggered = set()

    # Keyword match pass
    for mod, data in modules_config.items():
        if any(k in text for k in data["keywords"]):
            responses.append({
                "module": mod,
                "response": data["response"],
                "match_type": "keyword"
            })
            triggered.add(mod)
            await safe_session_append(session_id, mod)
            log_module_and_tone(session_id, mod, "from_keyword")

    # Semantic fallback pass
    if not triggered:
        match = encode_and_match_semantic(text)
        if match:
            responses.append({
                "module": match,
                "response": modules_config[match]["response"],
                "match_type": "semantic"
            })
            triggered.add(match)
            await safe_session_append(session_id, match)
            log_module_and_tone(session_id, match, "from_semantic")

    # Soft fallback if still unhandled
    if not triggered:
        fallback = soft_mirror_fallback()
        fallback["match_type"] = "soft_fallback"
        responses.append(fallback)
        await safe_session_append(session_id, "soft_mirror")
        log_module_and_tone(session_id, "soft_mirror", "fallback")

    return responses
