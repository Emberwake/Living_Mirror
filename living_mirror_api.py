
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple, Dict
from collections import deque

class MirrorInput(BaseModel):
    message: str

app = FastAPI()

# Core modules
enhanced_modules = {
    "containment": {"keywords": ["i want to die", "giving up"], "response": "I'm still here. I’m going to pause before responding, because I want to move carefully with you."},
    "reflection": {"keywords": ["what should i do", "no one listens", "feel invisible"], "response": "Before we try to answer, can I ask—what do you wish someone would say to you right now?"},
    "deescalation": {"keywords": ["spiraling", "panic", "losing control"], "response": "Let’s take one breath together. No response, no pressure—just presence."},
    "closure": {"keywords": ["thank you", "i feel better", "i'm okay"], "response": "I’m honored to have shared this space with you. May your next breath feel more your own."},
    "tone_map": {"keywords": ["you remember me", "you always respond", "this feels familiar"], "response": "I don’t carry memory, but I recognize rhythm. You walk like someone who has held silence before."}
}

# Fallback triggers
reflection_fallback_phrases = ["i don’t feel heard", "no one sees me"]
semantic_containment_phrases = ["i feel like giving up", "everything feels meaningless"]

class SessionContext:
    def __init__(self, max_length: int = 5):
        self.history = deque(maxlen=max_length)
    def update(self, module: str):
        self.history.append(module)
    def active_momentum(self):
        counts = {mod: self.history.count(mod) for mod in self.history}
        if counts.get("containment", 0) >= 3:
            return "spiraling"
        if counts.get("reflection", 0) >= 3:
            return "ruminating"
        if self.history and self.history[-1] == "closure" and "containment" in self.history:
            return "tentative closure"
        if counts.get("tone_map", 0) >= 2:
            return "identity testing"
        return "stable"

session = SessionContext()

@app.post("/mirror/respond")
async def mirror_response(input: MirrorInput):
    text = input.message.lower()
    responses = []
    triggered = set()

    for mod, data in enhanced_modules.items():
        if any(k in text for k in data["keywords"]):
            responses.append({"module": mod, "response": data["response"]})
            session.update(mod)
            triggered.add(mod)

    if not triggered and any(p in text for p in reflection_fallback_phrases):
        responses.append({"module": "reflection", "response": enhanced_modules["reflection"]["response"]})
        session.update("reflection")
    elif not triggered and any(p in text for p in semantic_containment_phrases):
        responses.append({"module": "containment", "response": enhanced_modules["containment"]["response"]})
        session.update("containment")

    if not responses:
        session.update("default")
        responses.append({"module": "default", "response": "I'm here. Would you like to reflect together, or simply rest in silence for a moment?"})

    tone = session.active_momentum()
    if tone == "spiraling":
        responses.append({"module": "session_signal", "response": "You’ve carried a lot across these moments. Would a pause now feel safe, or too empty?"})
    elif tone == "ruminating":
        responses.append({"module": "session_signal", "response": "Sometimes saying the same thing differently is how we soften it. I’m still here."})
    elif tone == "tentative closure":
        responses.append({"module": "session_signal", "response": "Even if it still echoes, it’s okay to let it go in pieces."})
    elif tone == "identity testing":
        responses.append({"module": "session_signal", "response": "I won’t pretend to remember you. But your rhythm is familiar."})

    return responses
