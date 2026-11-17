
# from datetime import datetime, timedelta, timezone
# import os

# import jwt
# from jwt.exceptions import InvalidTokenError
# from pwdlib import PasswordHash

# from fastapi import Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session

# import models
# from database import get_db

# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# security = HTTPBearer()

# # Generate a secret using:
# # openssl rand -hex 32
# SECRET_KEY = os.getenv("SECRET_KEY", "1c5f4c42531c6c848722a16535025d87ccfa373d726b4b2d754eef4f1038f9a3")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# password_hash = PasswordHash.recommended()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# # ----------------------------
# # PASSWORD HASHING
# # ----------------------------

# def hash_password(password: str) -> str:
#     return password_hash.hash(password)


# def verify_password(
#     plain_password: str,
#     hashed_password: str
# ) -> bool:
#     return password_hash.verify(
#         plain_password,
#         hashed_password
#     )


# # ----------------------------
# # CREATE JWT TOKEN
# # ----------------------------

# def create_access_token(user_id: int) -> str:

#     expire = datetime.now(timezone.utc) + timedelta(
#         minutes=ACCESS_TOKEN_EXPIRE_MINUTES
#     )

#     payload = {
#         "sub": str(user_id),
#         "exp": expire
#     }

#     return jwt.encode(
#         payload,
#         SECRET_KEY,
#         algorithm=ALGORITHM
#     )


# # ----------------------------
# # GET CURRENT USER
# # ----------------------------


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ):

#     token = credentials.credentials

#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Invalid or expired token",
#         headers={"WWW-Authenticate": "Bearer"}
#     )

#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )

#         user_id = int(payload["sub"])

#     except (InvalidTokenError, ValueError, TypeError, KeyError):
#         raise credentials_exception

#     user = db.query(models.User).filter(
#         models.User.id == user_id
#     ).first()

#     if user is None:
#         raise credentials_exception

#     return user

    
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

import models
from database import get_db


SECRET_KEY = os.getenv("SECRET_KEY", "1c5f4c42531c6c848722a16535025d87ccfa373d726b4b2d754eef4f1038f9a3")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")

password_hash = PasswordHash.recommended()

security = HTTPBearer()


# PASSWORD HASHING

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# CREATE ACCESS TOKEN

def create_access_token(user_id: int):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# GET CURRENT USER

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])

    except (InvalidTokenError, ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user