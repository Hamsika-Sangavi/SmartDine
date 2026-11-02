import os
import sys
import datetime

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
TOKEN_DAYS = 7


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


def _secret():
    secret = os.getenv("JWT_SECRET", "smartdine-dev-secret")
    if not secret:
        raise HTTPException(status_code=500, detail="Server login is not configured")
    return secret


def _make_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=TOKEN_DAYS),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def _hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        raise HTTPException(status_code=400, detail="Password is too long")
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def _check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], hashed.encode("utf-8"))
    except ValueError:
        return False


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds is None:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        payload = jwt.decode(creds.credentials, _secret(), algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired login")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired login")
    return user


@router.post("/auth/signup")
def signup(req: SignupRequest):
    email = req.email.lower()
    password_hash = _hash_password(req.password)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=409, detail="This email is already registered")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (req.name.strip(), email, password_hash),
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while creating account")
    return {
        "token": _make_token(user_id),
        "user": {"id": user_id, "name": req.name.strip(), "email": email},
    }


@router.post("/auth/login")
def login(req: LoginRequest):
    email = req.email.lower()
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while logging in")
    if not user or not _check_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {
        "token": _make_token(user["id"]),
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }


@router.get("/auth/me")
def me(user=Depends(get_current_user)):
    return user


@router.get("/favourites")
def list_favourites(user=Depends(get_current_user)):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT r.* FROM favourites f JOIN restaurants r ON r.id = f.restaurant_id "
            "WHERE f.user_id = %s ORDER BY f.created_at DESC",
            (user["id"],),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while fetching favourites")
    return {"count": len(rows), "results": rows}


@router.post("/favourites/{restaurant_id}")
def add_favourite(restaurant_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM restaurants WHERE id = %s", (restaurant_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Restaurant not found")
        cursor.execute(
            "INSERT IGNORE INTO favourites (user_id, restaurant_id) VALUES (%s, %s)",
            (user["id"], restaurant_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while saving favourite")
    return {"saved": True, "restaurant_id": restaurant_id}


@router.delete("/favourites/{restaurant_id}")
def remove_favourite(restaurant_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM favourites WHERE user_id = %s AND restaurant_id = %s",
            (user["id"], restaurant_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while removing favourite")
    return {"saved": False, "restaurant_id": restaurant_id}