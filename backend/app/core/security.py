import hashlib
import hmac
import os
import json
import base64
import time
from typing import Optional, Dict, Any
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    """Generates a secure salted hash of the password using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return f"{salt}${pwd_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored salted hash."""
    try:
        salt, expected_hash = hashed_password.split("$", 1)
        calc_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return hmac.compare_digest(calc_hash, expected_hash)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta_minutes: Optional[int] = None) -> str:
    """Creates a standard signed JWT token."""
    expire_minutes = expires_delta_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    payload = data.copy()
    payload["exp"] = int(time.time()) + (expire_minutes * 60)
    payload["iat"] = int(time.time())
    
    header = {"alg": ALGORITHM, "typ": "JWT"}
    
    def b64_encode(obj):
        json_bytes = json.dumps(obj, separators=(',', ':')).encode('utf-8')
        return base64.urlsafe_b64encode(json_bytes).decode('utf-8').rstrip('=')
    
    header_b64 = b64_encode(header)
    payload_b64 = b64_encode(payload)
    
    message = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies and decodes a signed JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        message = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)).decode('utf-8')
        payload = json.loads(payload_json)
        
        if payload.get("exp") and payload["exp"] < time.time():
            return None  # Token expired
            
        return payload
    except Exception:
        return None
