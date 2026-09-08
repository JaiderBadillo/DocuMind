import sqlite3
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .config import DATABASE_PATH, BASE_DIR

SEED_DB_PATH = BASE_DIR / "documind_seed.db"

_DB_INITIALIZED = False

def get_db_connection():
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
    except Exception:
        pass
    return conn

def init_database():
    global _DB_INITIALIZED
    
    target_path = Path(DATABASE_PATH)
    if not target_path.exists() or target_path.stat().st_size < 10000:
        if SEED_DB_PATH.exists():
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(str(SEED_DB_PATH), str(target_path))
                print(f"[DB] Initialized database from seed: {SEED_DB_PATH} -> {target_path}")
            except Exception as e:
                print(f"[DB] Could not copy seed db: {e}")
                
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Users table (case-insensitive email)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE COLLATE NOCASE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'ADMIN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_nocase ON users(email COLLATE NOCASE)")
        
        # 2. Repositories table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 3. Documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_extension TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            processing_status TEXT DEFAULT 'PENDING',
            raw_text TEXT,
            content_html TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
        )
        """)
        
        # Auto-migration for content_html in existing databases
        cursor.execute("PRAGMA table_info(documents)")
        cols = [r["name"] for r in cursor.fetchall()]
        if "content_html" not in cols:
            cursor.execute("ALTER TABLE documents ADD COLUMN content_html TEXT")
        
        
        # 4. Document Metadata table (AI extraction)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER UNIQUE NOT NULL,
            category TEXT NOT NULL,
            category_confidence REAL NOT NULL,
            executive_summary TEXT NOT NULL,
            extracted_entities_json TEXT NOT NULL,
            token_count INTEGER DEFAULT 0,
            word_count INTEGER DEFAULT 0,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """)
        
        # 5. Document Chunks table (RAG & Vector Search)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding_json TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """)
        
        # 6. Audit Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            document_id INTEGER,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Automatically seed default admin if missing
        cursor.execute("SELECT id FROM users WHERE email = 'admin@documind.com'")
        if not cursor.fetchone():
            from .security import hash_password
            pwd = hash_password("Admin123!")
            cursor.execute(
                "INSERT INTO users (email, full_name, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin@documind.com", "Administrador DocuMind", pwd, "ADMIN")
            )
            admin_id = cursor.lastrowid
            default_repos = [
                ("Contratos y Acuerdos Legales", "Repositorio de minutas, contratos de prestación de servicios y confidencialidad."),
                ("Facturación y Finanzas", "Comprobantes fiscales, facturas electrónicas y órdenes de compra."),
                ("Talento Humano y Selección", "Hojas de vida de candidatos, perfiles de competencias y certificaciones."),
                ("Informes Técnicos de TI", "Arquitectura de software, planes de contingencia y manuales de operaciones.")
            ]
            for name, desc in default_repos:
                cursor.execute(
                    "INSERT INTO repositories (user_id, name, description) VALUES (?, ?, ?)",
                    (admin_id, name, desc)
                )
        conn.commit()
        _DB_INITIALIZED = True
    except Exception as e:
        conn.rollback()
        print(f"Error inicializando base de datos: {e}")
    finally:
        conn.close()

@contextmanager
def get_db():
    global _DB_INITIALIZED
    if not _DB_INITIALIZED:
        init_database()
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def log_audit(action: str, status: str, details: str = "", user_id: Optional[int] = None, document_id: Optional[int] = None, conn: Optional[sqlite3.Connection] = None):
    try:
        if conn:
            conn.execute(
                "INSERT INTO audit_logs (user_id, document_id, action, status, details) VALUES (?, ?, ?, ?, ?)",
                (user_id, document_id, action, status, details)
            )
        else:
            with get_db() as c:
                c.execute(
                    "INSERT INTO audit_logs (user_id, document_id, action, status, details) VALUES (?, ?, ?, ?, ?)",
                    (user_id, document_id, action, status, details)
                )
    except Exception as e:
        print(f"Error logging audit event: {e}")

def sync_user_to_seed_db(user_id: int):
    """Sync registered user and repositories to SEED_DB_PATH so they survive fresh deployments."""
    try:
        if not SEED_DB_PATH.exists() or str(SEED_DB_PATH.resolve()) == str(Path(DATABASE_PATH).resolve()):
            return
        with get_db_connection() as src_conn:
            src_cur = src_conn.cursor()
            src_cur.execute("SELECT id, email, full_name, password_hash, role, created_at FROM users WHERE id = ?", (user_id,))
            u = src_cur.fetchone()
            if not u:
                return
            src_cur.execute("SELECT name, description FROM repositories WHERE user_id = ?", (user_id,))
            repos = src_cur.fetchall()

        seed_conn = sqlite3.connect(str(SEED_DB_PATH), timeout=30.0)
        try:
            s_cur = seed_conn.cursor()
            s_cur.execute("SELECT id FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))", (u["email"],))
            existing = s_cur.fetchone()
            if not existing:
                s_cur.execute(
                    "INSERT INTO users (id, email, full_name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (u["id"], u["email"], u["full_name"], u["password_hash"], u["role"], u["created_at"])
                )
                seed_uid = u["id"]
                for r in repos:
                    s_cur.execute(
                        "INSERT INTO repositories (user_id, name, description) VALUES (?, ?, ?)",
                        (seed_uid, r["name"], r["description"])
                    )
                seed_conn.commit()
                print(f"[DB Sync] Successfully synced user {u['email']} to seed DB")
        finally:
            seed_conn.close()
    except Exception as e:
        print(f"[DB Sync] Warning syncing user to seed DB: {e}")
