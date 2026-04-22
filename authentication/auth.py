from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()
#initialize the router
#prefix means all endpoints here will start with "/auth"
router=APIRouter(prefix="/auth", tags=["Authentication"])

#configuration and mock users DB
SECRET_KEY:str=os.environ.get("SECRET_KEY", "")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

fake_users_db: dict[Any, Any]={}
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="auth/login")

#Pydantic Models
class User(BaseModel):
    username:str
    email:EmailStr | None = None

class UserInDB(User):
    hashed_password:str

class Token(BaseModel):
    access_token:str
    token_type:str

#helper functions

def truncate_password_to_72_bytes(password: str) -> str:
    """Truncate password to 72 bytes (bcrypt limit) at byte level"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes, handling incomplete UTF-8 sequences
        truncated = password_bytes[:72]
        # Decode with error handling and re-encode to ensure it's valid and under 72 bytes
        decoded = truncated.decode('utf-8', errors='ignore')
        return decoded
    return password

def verify_password(plain_password:str,hashed_password:str):
    truncated = truncate_password_to_72_bytes(plain_password)
    return pwd_context.verify(truncated, hashed_password)

def get_password_hash(plain_password:str):
    truncated = truncate_password_to_72_bytes(plain_password)
    print("truncated==", truncated)
    return pwd_context.hash(truncated)

def create_access_token(data:Any):
    jwt_data=data.copy()
    expiresAt=datetime.now(timezone.utc)+timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_data.update({"exp":expiresAt})
    return jwt.encode(claims=jwt_data,key=SECRET_KEY,algorithm=ALGORITHM)

#create a dependency to check if the user really exists in our dataase and only if it is True then all the endpoints in main.py are accessible by the user
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    #create a custom exception to handle credentials exception
    credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload=jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username:str|None=payload.get("sub", None)
        if username is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    #crucial step, the token might be valid but what if the user deleted their account 5 mins ago? check the database if the uer exists.
    user_dict =fake_users_db.get(username)
    if user_dict is None:
        raise credential_exception
    
    return User(**user_dict)

#endpoints (using @router instead of @app)
#1.allow the user to register
@router.post("/register")
def register_user(username:str, email:str, password:str):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="USer already exists")
    
    fake_users_db[username]={
     "username":username,
     "email": email,
     "hashed_password": get_password_hash(password)    
     }
    
    return JSONResponse(status_code=201, content={"msg":"User Registered Successfully"})

#allow the user to login once the registration is complete
@router.post("/login", response_model=Token)
def user_login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict=fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    userModel=UserInDB(**user_dict)

    if not verify_password(form_data.password, userModel.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    #once the details are verified, create an Access token
    access_token=create_access_token(data={"sub":userModel.username})
    return {"access_token":access_token, "token_type":"bearer"}

#authorization check -> uses dependency injection
@router.get("/me")
def check_validity(data:Annotated[str, Depends(get_current_user)]):
    return "Valid details"