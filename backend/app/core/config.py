import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DATABASE_PATH = BASE_DIR / "documind.db"
DOCS_DIR = BASE_DIR.parent / "test_dataset_30_docs"

# Ensure storage directory exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "documind_secret_key_uts_enterprise_2026_super_secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

ENV_FILE = BASE_DIR / ".env"

# AI Configuration
def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        for env_path in [ENV_FILE, BASE_DIR.parent / ".env"]:
            if env_path.exists():
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("GEMINI_API_KEY="):
                                k = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                                if k:
                                    key = k
                                    os.environ["GEMINI_API_KEY"] = key
                                    return key
                except Exception:
                    pass
    return key

def set_gemini_api_key(key: str):
    clean_key = key.strip()
    os.environ["GEMINI_API_KEY"] = clean_key
    try:
        lines = []
        found = False
        if ENV_FILE.exists():
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Error guardando .env: {e}")

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

from typing import List, Tuple, Optional

_CACHED_GEMINI_MODEL = None

def get_gemini_candidate_models(genai=None) -> List[str]:
    """Returns an ordered list of candidate Gemini models, prioritizing gemini-3.6-flash and stable models,
    filtering out deprecated 2.5 models."""
    priority = [
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    if not genai:
        return priority

    try:
        available = []
        for m in genai.list_models():
            methods = getattr(m, 'supported_generation_methods', [])
            if 'generateContent' in methods:
                clean = m.name.replace('models/', '')
                # Filter out models known to be discontinued/deprecated for new users (gemini-2.5)
                if not clean.startswith('gemini-2.5') and 'tts' not in clean:
                    available.append(clean)
        
        # Order available by priority first
        ordered = [p for p in priority if p in available]
        for a in available:
            if a not in ordered:
                ordered.append(a)
        if ordered:
            return ordered
    except Exception as e:
        print(f"Error listando modelos Gemini: {e}")
        
    return priority

def get_best_gemini_model(genai=None) -> str:
    """Dynamically identifies and returns the highest-tier supported Gemini model for this API key."""
    global _CACHED_GEMINI_MODEL
    if _CACHED_GEMINI_MODEL:
        return _CACHED_GEMINI_MODEL
    candidates = get_gemini_candidate_models(genai)
    return candidates[0] if candidates else "gemini-3.6-flash"

def generate_with_gemini_fallback(genai, prompt: str) -> Tuple[str, str]:
    """Tries generating content with candidate models in priority order until one succeeds.
    Returns (response_text, model_name_used)."""
    global _CACHED_GEMINI_MODEL
    candidates = get_gemini_candidate_models(genai)
    
    if _CACHED_GEMINI_MODEL and _CACHED_GEMINI_MODEL in candidates:
        candidates.remove(_CACHED_GEMINI_MODEL)
        candidates.insert(0, _CACHED_GEMINI_MODEL)
        
    last_err = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt)
            if resp and hasattr(resp, "text") and resp.text:
                _CACHED_GEMINI_MODEL = model_name
                return resp.text.strip(), model_name
        except Exception as ex:
            last_err = ex
            print(f"Modelo {model_name} falló: {ex}. Probando siguiente alternativa...")
            continue
            
    if last_err:
        raise last_err
    raise RuntimeError("No se pudo obtener respuesta con ningún modelo Gemini disponible.")

