from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from ..models.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from ..core.security import hash_password, verify_password, create_access_token, decode_access_token
from ..core.database import get_db, log_audit

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización ausente o inválido")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token expirado o firma inválida")
    return payload

@router.post("/register", response_model=TokenResponse)
def register_user(user: UserCreate):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
            
        hashed_pwd = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (email, full_name, password_hash, role) VALUES (?, ?, ?, ?)",
            (user.email, user.full_name, hashed_pwd, "USER")
        )
        user_id = cursor.lastrowid
        
        default_repos = [
            ("Contratos y Acuerdos Legales", "Repositorio de minutas, contratos de prestación de servicios y confidencialidad."),
            ("Facturación y Finanzas", "Comprobantes fiscales, facturas electrónicas y órdenes de compra."),
            ("Talento Humano y Selección", "Hojas de vida de candidatos, perfiles de competencias y certificaciones."),
            ("Informes Técnicos de TI", "Arquitectura de software, planes de contingencia y manuales de operaciones.")
        ]
        for name, desc in default_repos:
            cursor.execute(
                "INSERT INTO repositories (user_id, name, description) VALUES (?, ?, ?)",
                (user_id, name, desc)
            )
        
        cursor.execute("SELECT id, email, full_name, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        token = create_access_token({"sub": row["email"], "user_id": row["id"], "role": row["role"]})
        log_audit("USER_REGISTER", "SUCCESS", f"Usuario {user.email} registrado exitosamente", user_id=user_id)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
                "role": row["role"],
                "created_at": str(row["created_at"])
            }
        }

@router.post("/login", response_model=TokenResponse)
def login_user(creds: UserLogin):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, password_hash, role, created_at FROM users WHERE email = ?", (creds.email,))
        row = cursor.fetchone()
        
        if not row or not verify_password(creds.password, row["password_hash"]):
            log_audit("USER_LOGIN_FAILED", "WARNING", f"Intento fallido de login para: {creds.email}")
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        token = create_access_token({"sub": row["email"], "user_id": row["id"], "role": row["role"]})
        log_audit("USER_LOGIN", "SUCCESS", f"Sesión iniciada por {creds.email}", user_id=row["id"])
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
                "role": row["role"],
                "created_at": str(row["created_at"])
            }
        }

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, role, created_at FROM users WHERE id = ?", (current_user["user_id"],))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "id": row["id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "role": row["role"],
            "created_at": str(row["created_at"])
        }

from pydantic import BaseModel

class GeminiKeyPayload(BaseModel):
    api_key: str

@router.get("/gemini-key")
def get_gemini_key_status(current_user: dict = Depends(get_current_user)):
    from ..core.config import get_gemini_api_key
    k = get_gemini_api_key()
    return {
        "active": bool(k),
        "masked_key": f"{k[:6]}...{k[-4:]}" if len(k) > 10 else ("Configurada" if k else "No configurada")
    }

@router.post("/gemini-key")
def set_gemini_key(payload: GeminiKeyPayload, current_user: dict = Depends(get_current_user)):
    from ..core.config import set_gemini_api_key
    set_gemini_api_key(payload.api_key)
    log_audit("CONFIG_UPDATE", "SUCCESS", "Clave API de Google Gemini configurada", user_id=current_user["user_id"])
    return {"message": "Clave API de Google Gemini actualizada con éxito", "active": bool(payload.api_key.strip())}
