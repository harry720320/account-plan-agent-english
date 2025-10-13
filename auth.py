"""
User Authentication Module
Handles user login, password hashing, JWT token and other functions
"""
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User
from config import settings

# JWT Key (Production environment should use more secure key)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Use SHA-256 to hash password"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """ValidatePassword"""
    try:
        salt, password_hash = hashed_password.split(":")
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def create_access_token(data: Dict[str, Any]) -> str:
    """CreateJWTAccessToken"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """ValidateJWTToken"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Validate user credentials"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get current user from token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    username = payload.get("sub")
    if username is None:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

def init_admin_user(db: Session) -> bool:
    """Initialize administrator user"""
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            return True
        
        # Create admin user
        admin_user = User(
            username="admin",
            password_hash=hash_password("admin"),
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        return True
        
    except Exception as e:
        print(f"Initialize administrator user failed: {e}")
        return False
