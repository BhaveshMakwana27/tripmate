from jose import jwt
from app.config import settings
from app import database,models,errors
from app.schemas import token_schema
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_TIMEOUT = settings.token_expire_timeout

oauth2_scheme = OAuth2PasswordBearer('user/login')

def create_token(data:dict):
    to_encode=data.copy()
    expire_time = datetime.utcnow() + timedelta(days=int(ACCESS_TOKEN_EXPIRE_TIMEOUT))
    to_encode.update({'exp':expire_time})
    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

def verify_access_token(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        id:str|None = payload.get('user_id')
        user_type:str|None = payload.get('user_type')
        if id is None:
            raise errors.CredentialsException
        token_data = token_schema.TokenData(id=id,user_type=user_type)
    except:
        raise errors.CredentialsException
    return token_data

def get_current_user_type(token:str=Depends(oauth2_scheme)):
    token = verify_access_token(token)
    return token.user_type

def get_current_user(token:str=Depends(oauth2_scheme),db:Session = Depends(database.get_db)):
    token = verify_access_token(token)
    user = db.query(models.User).filter(models.User.user_id==token.id).first()
    if user is None:
        raise errors.UserNotExistException
    return user
