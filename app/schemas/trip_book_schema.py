from pydantic import BaseModel,ConfigDict
from app.schemas import trip_schema,payment_schema,user_schema,base_schema
from typing import List

class TripBookBase(BaseModel):
    booking_id:int
    trip_id:int
    driver_id:int
    passenger_id:int
    booking_status:str
    payable_amount:int
    seat_count:int

    model_config = ConfigDict(from_attributes=True)
    
class CreateNewBooking(BaseModel):
    trip_id:int
    driver_id:int
    passenger_id:int
    payable_amount:int
    seat_count:int

class BookingStatus(BaseModel):
    booking_id:int
    booking_status:str

    model_config = ConfigDict(from_attributes=True)

class BookingStatusResponse(base_schema.BaseSchema):
    data : BookingStatus
    
class PassangerBookingList(BaseModel):
    booking_id : int
    payable_amount:int
    seat_count:int
    driver_name : str = None
    trip : trip_schema.TripDetailBase
    
    model_config = ConfigDict(from_attributes=True)

class PassangerBookingListResponse(base_schema.BaseSchema):
    data : List[PassangerBookingList]

class BookingDetail(BaseModel):
    user:user_schema.GetUser
    booking_details:TripBookBase
    payment_details:payment_schema.PaymentDetail
    trip:trip_schema.TripDetailBase

class BookingDetailResponse(base_schema.BaseSchema):
    data:BookingDetail
