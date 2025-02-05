from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os

# Router setup
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Secret key and algorithm (use environment variable for production)
SECRET_KEY = os.getenv("SECRET_KEY", "f8902aab98f24c60b764c3c28b5bb91e")  # Use environment variable
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Pydantic models
class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Create user endpoint
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # Check if user already exists
    existing_user = db.query(Users).filter(Users.username == create_user_request.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered.")
    
    # Hash the password and create the user model
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )
    
    # Add user to the session and commit
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)  # Refresh the instance to get the updated data (e.g., ID)

    # Return the created user's info (without the password)
    return {
        "id": create_user_model.id,
        "username": create_user_model.username,
    }

# Login and token generation endpoint
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    token = create_access_token(user.username, user.id, timedelta(minutes=30))  # 30 mins expiration
    return {'access_token': token, 'token_type': "bearer"}

# User authentication function
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# Token creation function
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token or user.')
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found.')
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token or user.')