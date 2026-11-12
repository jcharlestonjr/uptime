"""Authentication: API keys + JWT for dashboard."""

from __future__ import annotations

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session

from .database import get_db
from .models import ApiKey, User
from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer = HTTPBearer(auto_error=False)


def generate_api_key() -> str:
    return "up_" + secrets.token_urlsafe(32)


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key: str, db: Session) -> Optional[User]:
    if not key:
        return None
    ak = db.query(ApiKey).filter(ApiKey.key == key, ApiKey.revoked == False).first()
    if not ak:
        return None
    return db.query(User).filter(User.id == ak.user_id).first()


def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    creds: Optional[HTTPAuthorizationCredentials] = Security(bearer),
    db: Session = Depends(get_db),
) -> User:
    # Try API key first
    if api_key:
        user = verify_api_key(api_key, db)
        if user:
            return user
    # Try JWT bearer
    if creds:
        # Simple JWT decode (production: use python-jose)
        try:
            import jwt as pyjwt
            payload = pyjwt.decode(creds.credentials, settings.secret_key, algorithms=["HS256"])
            user = db.query(User).filter(User.id == payload.get("sub")).first()
            if user:
                return user
        except Exception:
            pass
    raise HTTPException(status_code=401, detail="Invalid or missing authentication")


def create_user(db: Session, email: str, name: str = None, password: str = None) -> User:
    user = User(email=email, name=name)
    if password:
        import bcrypt
        user.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_api_key(db: Session, user: User, name: str = "default") -> str:
    key = generate_api_key()
    ak = ApiKey(key=key, user_id=user.id, name=name)
    db.add(ak)
    db.commit()
    return key


def create_jwt(user: User) -> str:
    import jwt as pyjwt
    payload = {
        "sub": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=7) if False else __import__("datetime").datetime.utcnow() + timedelta(days=7),
    }
    return pyjwt.encode(payload, settings.secret_key, algorithm="HS256")