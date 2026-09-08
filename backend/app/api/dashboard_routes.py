from fastapi import APIRouter, Depends
from typing import List
from ..models.schemas import DashboardStatsResponse, AuditLogItem
from ..core.database import get_db
from .auth_routes import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard y Métricas"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        is_admin = current_user.get("role") == "ADMIN"
        user_id = current_user.get("user_id")
        
        # 1. Total documents & storage
        if is_admin:
            cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(file_size_bytes), 0) as total_size FROM documents")
            doc_stat = cursor.fetchone()
            total_docs = doc_stat["count"] or 0
            total_bytes = doc_stat["total_size"] or 0
            
            cursor.execute("SELECT COUNT(*) as count FROM repositories")
            total_repos = cursor.fetchone()["count"] or 0
            
            cursor.execute("SELECT processing_status, COUNT(*) as count FROM documents GROUP BY processing_status")
            status_rows = cursor.fetchall()
            
            cursor.execute("""
            SELECT COALESCE(m.category, 'SIN_CLASIFICAR') as category, COUNT(*) as count
            FROM documents d
            LEFT JOIN document_metadata m ON d.id = m.document_id
            GROUP BY category
            """)
            cat_rows = cursor.fetchall()
            
            cursor.execute("SELECT file_extension, COUNT(*) as count FROM documents GROUP BY file_extension")
            fmt_rows = cursor.fetchall()
        else:
            cursor.execute("""
            SELECT COUNT(d.id) as count, COALESCE(SUM(d.file_size_bytes), 0) as total_size
            FROM documents d
            JOIN repositories r ON d.repository_id = r.id
            WHERE r.user_id = ?
            """, (user_id,))
            doc_stat = cursor.fetchone()
            total_docs = doc_stat["count"] or 0
            total_bytes = doc_stat["total_size"] or 0
            
            cursor.execute("SELECT COUNT(*) as count FROM repositories WHERE user_id = ?", (user_id,))
            total_repos = cursor.fetchone()["count"] or 0
            
            cursor.execute("""
            SELECT d.processing_status, COUNT(*) as count
            FROM documents d
            JOIN repositories r ON d.repository_id = r.id
            WHERE r.user_id = ?
            GROUP BY d.processing_status
            """, (user_id,))
            status_rows = cursor.fetchall()
            
            cursor.execute("""
            SELECT COALESCE(m.category, 'SIN_CLASIFICAR') as category, COUNT(*) as count
            FROM documents d
            JOIN repositories r ON d.repository_id = r.id
            LEFT JOIN document_metadata m ON d.id = m.document_id
            WHERE r.user_id = ?
            GROUP BY category
            """, (user_id,))
            cat_rows = cursor.fetchall()
            
            cursor.execute("""
            SELECT d.file_extension, COUNT(*) as count
            FROM documents d
            JOIN repositories r ON d.repository_id = r.id
            WHERE r.user_id = ?
            GROUP BY d.file_extension
            """, (user_id,))
            fmt_rows = cursor.fetchall()

        status_dict = {"PENDING": 0, "PROCESSING": 0, "COMPLETED": 0, "FAILED": 0}
        for r in status_rows:
            status_dict[r["processing_status"]] = r["count"]
            
        categories = []
        for r in cat_rows:
            count = r["count"]
            pct = round((count / total_docs * 100), 1) if total_docs > 0 else 0.0
            categories.append({
                "category": r["category"],
                "count": count,
                "percentage": pct
            })
            
        formats = [
            {"extension": r["file_extension"].upper(), "count": r["count"]}
            for r in fmt_rows
        ]
        
        return {
            "total_documents": total_docs,
            "total_repositories": total_repos,
            "total_storage_bytes": total_bytes,
            "status_counts": status_dict,
            "categories": categories,
            "formats": formats
        }

@router.get("/logs", response_model=List[AuditLogItem])
def get_audit_logs(limit: int = 20, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        is_admin = current_user.get("role") == "ADMIN"
        if is_admin:
            cursor.execute("""
            SELECT id, action, status, details, timestamp
            FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT ?
            """, (limit,))
        else:
            cursor.execute("""
            SELECT id, action, status, details, timestamp
            FROM audit_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """, (current_user["user_id"], limit))
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "action": r["action"],
                "status": r["status"],
                "details": r["details"],
                "timestamp": str(r["timestamp"])
            }
            for r in rows
        ]
