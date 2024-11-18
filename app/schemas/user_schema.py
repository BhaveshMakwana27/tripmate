from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime
from app.enums import Gender
from .token_schema import Token
from . import base_schema,user_schema
from typing import List,Union

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
    
    model_config = ConfigDict(from_attributes=True)

class EditProfile(BaseModel):
    name:str
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

    model_config = ConfigDict(from_attributes=True)

class CreateUser(UserBase):
    password:str

class DriverBase(BaseModel):
    user_id:int
    name:str

    model_config = ConfigDict(from_attributes=True)

class GetPassengerUserDetails(UserBase):
    profile_photo:str
    created_at:datetime

    class Config:
        orm_mode = True

class GetDriverUserDetails(UserBase):
    ratings:float
    rating_count:int
    profile_photo:str
    created_at:datetime
    documents:List[str] = []

    model_config = ConfigDict(from_attributes=True)
        
class UploadUserDocs(BaseModel):
    user_id:int
    aadhar_number:str
    aadhar_card_front:str
    aadhar_card_back:str
    license_front:str
    license_back:str

class PassengerDetailBase(BaseModel):
    booking_id : int
    name : str
    seat_count : int
    payable_amount : int


class DriverDetailBase(BaseModel):
    user_id:int
    name:str
    email:str
    contact_no:str
    profile_photo:str
    ratings:float
    rating_count:int

    class Config:
        orm_mode=True

class GetProfileDetailsResponse(base_schema.BaseSchema):
    data : Union[user_schema.GetPassengerUserDetails,user_schema.GetDriverUserDetails]
