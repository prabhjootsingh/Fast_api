
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import models
import schemas

from database import engine, get_db
from response import success_response, error_response

from auth import hash_password, verify_password, create_access_token
from auth import get_current_user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

security = HTTPBearer()


# --------------------------------
# GLOBAL EXCEPTION HANDLERS
# --------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):

    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    return error_response(
        message="Validation failed",
        status_code=422,
        data=exc.errors()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):

    return error_response(
        message="Internal server error",
        status_code=500
    )


# --------------------------------
# AUTHENTICATION DEPENDENCY
# --------------------------------

from auth import get_current_user


# --------------------------------
# HOME API
# --------------------------------

@app.get("/")
def home():

    return success_response(
        message="Welcome to FastAPI",
        data=None
    )


# --------------------------------
# REGISTER USER
# --------------------------------

@app.post("/users", status_code=201)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        age=user.age,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return success_response(
        message="User created successfully",
        data=schemas.UserResponse.model_validate(new_user).model_dump(),
        status_code=201
    )


# --------------------------------
# LOGIN API
# --------------------------------

@app.post("/login")
def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    if not user or not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return success_response(
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": schemas.UserResponse.model_validate(user).model_dump()
        }
    )


# --------------------------------
# GET ALL USERS
# --------------------------------

@app.get("/users")
def get_users(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    users = db.query(models.User).all()

    user_data = [
        schemas.UserResponse.model_validate(user).model_dump()
        for user in users
    ]

    return success_response(
        message="Users fetched successfully",
        data=user_data
    )
    # --------------------------------
# GET LOGGED-IN USER
# PROTECTED API
# --------------------------------
@app.get("/users/me")
def get_logged_in_user(
    current_user: models.User = Depends(get_current_user)
):
    return success_response(
        message="User fetched successfully",
        data=schemas.UserResponse.model_validate(
            current_user
        ).model_dump()
    )
# --------------------------------
# GET USER BY ID
# --------------------------------

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return success_response(
        message="User fetched successfully",
        data=schemas.UserResponse.model_validate(user).model_dump()
    )
