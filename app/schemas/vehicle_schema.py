from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas import user_schema

class VehicleBase(BaseModel):
    vehicle_id:int
    type :str
    model :str
    seat_capacity :int
    registration_number :str

    class Config:
        orm_mode=True

class UploadVehicle(BaseModel):
    type :str
    model :str
    seat_capacity :int
    registration_number :str
    rc_book_front :str
    rc_book_back :str

class VehicleList(BaseModel):
    Vehicle:VehicleBase
    image_path:str
    
class VehicleImages(BaseModel):
    images:List[str]

class VehicleDetails(VehicleBase):
    rc_book_front :str
    rc_book_back :str
    images:List[str]
    
class VehicleType(BaseModel):
    type:str

    class Config:
        orm_mode=True