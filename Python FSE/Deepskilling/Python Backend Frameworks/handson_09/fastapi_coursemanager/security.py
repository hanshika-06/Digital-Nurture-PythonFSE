from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
import bcrypt

# JWT configuration
SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""
================================================================================
BCRYPT PREFERENCE OVER MD5 OR SHA-256 (Task 1, Step 89)
================================================================================
Bcrypt is intentionally preferred over MD5 or SHA-256 for password hashing for
several key security reasons:

1. Slowness & CPU/GPU resistance:
   - MD5 and SHA-256 are cryptographic hash functions designed to be extremely fast.
     This speed makes them highly vulnerable to brute-force and dictionary attacks,
     where attackers can calculate billions of hashes per second using modern GPUs.
   - Bcrypt implements a customizable work factor (rounds) that forces the algorithm
     to consume significant processing time and memory. This makes hardware-accelerated
     brute-force attacks computationally infeasible.

2. Salting built-in:
   - MD5/SHA-256 hashes do not require salts by default, allowing attackers to pre-compute
     lookup databases (Rainbow Tables) to quickly decrypt common passwords.
   - Bcrypt automatically generates and incorporates a unique cryptographic salt for 
     every hash. This ensures that the same password hashed twice yields completely different 
     output values, neutralizing rainbow table attacks.
================================================================================
"""

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
