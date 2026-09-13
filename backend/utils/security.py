import os
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

if not os.environ.get("JWT_SECRET_KEY"):
    load_dotenv()

# JWT Settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-secret-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

# Password Hashing Settings
# Pepper is a secret key combined with the password before hashing
PASSWORD_PEPPER = os.environ.get("PASSWORD_PEPPER", "fallback-pepper-change-me-in-production")

def get_peppered_password(password: str) -> bytes:
    """Concatenates the password with the secret pepper and encodes to bytes."""
    return f"{password}{PASSWORD_PEPPER}".encode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a salted & peppered hash."""
    peppered_password = get_peppered_password(password=plain_password)
    # bcrypt expects the hashed_password to be bytes
    try:
        return bcrypt.checkpw(peppered_password, hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hashes the password with salt (bcrypt automatic) and pepper."""
    peppered_password = get_peppered_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(peppered_password, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
