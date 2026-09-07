from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.schemas import RepositoryCreate, RepositoryResponse
from ..core.database import get_db, log_audit
from .auth_routes import get_current_user

router = APIRouter(prefix="/repositories", tags=["Repositorios"])

@router.get("", response_model=List[RepositoryResponse])
def list_repositories(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT r.id, r.user_id, r.name, r.description, r.created_at,
               COUNT(d.id) AS document_count
        FROM repositories r
        LEFT JOIN documents d ON r.id = d.repository_id
        GROUP BY r.id
        ORDER BY r.created_at DESC
        """)
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "name": r["name"],
                "description": r["description"],
                "created_at": str(r["created_at"]),
                "document_count": r["document_count"]
            }
            for r in rows
        ]

@router.post("", response_model=RepositoryResponse)
def create_repository(repo: RepositoryCreate, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO repositories (user_id, name, description) VALUES (?, ?, ?)",
            (current_user["user_id"], repo.name.strip(), repo.description.strip())
        )
        repo_id = cursor.lastrowid
        cursor.execute("SELECT id, user_id, name, description, created_at FROM repositories WHERE id = ?", (repo_id,))
        row = cursor.fetchone()
        log_audit("REPO_CREATE", "SUCCESS", f"Repositorio '{repo.name}' creado", user_id=current_user["user_id"])
        
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "name": row["name"],
            "description": row["description"],
            "created_at": str(row["created_at"]),
            "document_count": 0
        }

@router.delete("/{repo_id}")
def delete_repository(repo_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM repositories WHERE id = ?", (repo_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Repositorio no encontrado")
            
        cursor.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
        log_audit("REPO_DELETE", "SUCCESS", f"Repositorio '{row['name']}' eliminado", user_id=current_user["user_id"])
        return {"message": "Repositorio y sus documentos eliminados correctamente"}
