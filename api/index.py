import sys
from pathlib import Path

# Configurar rutas para ejecución en entorno serverless
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from backend.app.main import app

# Export app instance for Vercel serverless function
