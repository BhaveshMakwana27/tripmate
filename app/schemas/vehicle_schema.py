from pydantic import BaseModel,ConfigDict
from typing import List
from datetime import datetime
from app.schemas import user_schema,base_schema

class VehicleBase(BaseModel):
    vehicle_id:int
    type :str
    model :str
    seat_capacity :int
    registration_number :str

class UploadVehicle(BaseModel):
    type :str
    model :str
    seat_capacity :int
    registration_number :str
    rc_book_front :str
    rc_book_back :str

class VehicleList(VehicleBase):
    image_path:str = None

    model_config = ConfigDict(from_attributes=True)

class VehicleListResponse(base_schema.BaseSchema):
    data : List[VehicleList]
    
class VehicleImages(BaseModel):
    images:List[str]

class VehicleDetails(VehicleBase):
    rc_book_front :str
    rc_book_back :str
    images:List[str]

class VehicleDetailResponse(base_schema.BaseSchema):
    data : VehicleDetails
    
class VehicleType(BaseModel):
    type:str

    model_config = ConfigDict(from_attributes=True)