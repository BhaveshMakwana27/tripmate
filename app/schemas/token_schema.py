from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import Optional,Union
from app import enums

class TokenData(BaseModel):
    id:Optional[int] = None
    user_type:Optional[enums.UserType] = None

class Token(BaseModel):
    access_token : str
    token_type : str
    need_docs : bool = False
