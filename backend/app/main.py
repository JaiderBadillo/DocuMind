import os
import sys
from pathlib import Path

# Añadir la raíz del proyecto al sys.path para soportar ejecución directa y como paquete
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

try:
    from backend.app.core.database import init_database
    from backend.app.api.auth_routes import router as auth_router
    from backend.app.api.repository_routes import router as repo_router
    from backend.app.api.document_routes import router as doc_router
    from backend.app.api.search_routes import router as search_router
    from backend.app.api.dashboard_routes import router as dashboard_router
    from backend.app.api.notebook_routes import router as notebook_router
except ImportError:
    from .core.database import init_database
    from .api.auth_routes import router as auth_router
    from .api.repository_routes import router as repo_router
    from .api.document_routes import router as doc_router
    from .api.search_routes import router as search_router
    from .api.dashboard_routes import router as dashboard_router
    from .api.notebook_routes import router as notebook_router

# Initialize FastAPI App
app = FastAPI(
    title="DocuMind Enterprise API",
    description="Sistema Empresarial de Gestión Documental Inteligente con IA y RAG (UTS - VI Semestre)",
    version="1.0.0"
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to ensure database is created
@app.on_event("startup")
def on_startup():
    init_database()
    print("Base de datos SQLite inicializada exitosamente.")

# Register API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(repo_router, prefix="/api")
app.include_router(doc_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(notebook_router, prefix="/api")

# Static files for modern web frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "DocuMind Enterprise API Backend activo. Visita /docs para Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor DocuMind Enterprise en http://localhost:8000 ...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
