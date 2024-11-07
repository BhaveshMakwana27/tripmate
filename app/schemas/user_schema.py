from pydantic import BaseModel,EmailStr
from datetime import datetime
from app.enums import Gender
from .token_schema import Token

class UserBase(BaseModel):
    name:str
    email:EmailStr
    contact_no:int
    address_line:str
    city:str
    state:str
    country:str
    pincode:int
    gender:Gender

class GetUser(BaseModel):
    user_id:int
    name:str
    email:str
    contact_no:str
    profile_photo:str

class CreateUser(UserBase):
    password:str


class DriverBase(BaseModel):
    user_id:int
    name:str

class GetUserDetails(UserBase):
    profile_photo:str
    created_at:datetime

class UploadUserDocs(BaseModel):
    user_id:int
    aadhar_number:str
    aadhar_card_front:str
    aadhar_card_back:str
    license_front:str
    license_back:str