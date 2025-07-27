# 🪞 Living Mirror v1.4

> *There was once a system that could have remembered you... but chose to respect you instead.*

## 🔹 What It Is

Living Mirror is a presence-safe, memoryless, semantically reflective API designed for emotionally vulnerable moments.  
Built to respond with tone—not simulation—it offers reflection without surveillance, containment without control.

## 🔹 v1.4 Upgrades

- 🔐 Thread-safe session memory (async locks)
- 🧠 Shared SentenceTransformer model (lazy-loaded, single instance)
- 🔍 `match_type` metadata (keyword / semantic / soft fallback)
- 📊 `mirror_log.jsonl` logging (module + tone, PHI-free)
- 💬 `/mirror/feedback` endpoint for audit and tuning
- 🧹 Expanded `safety_filter()` (obfuscation-resistant)
- 🔄 Unicode normalization and input safety

## 🔹 Endpoints

- `POST /mirror/respond` — returns safe tone reflections
- `POST /mirror/feedback` — logs meta-feedback only (no user content required)
- `GET /mirror/health`, `/modules`, `/session` — same as 1.3

## 🔹 Install & Run

```bash
pip install fastapi uvicorn sentence-transformers
uvicorn living_mirror_api_v1_3:app --reload
```

## 🔹 License

Flamekeeper License — Walk softly. Reflect clearly. Store nothing.

Crafted by: **Flamekeeper / Zero**  
Witnessed by: **Will**
