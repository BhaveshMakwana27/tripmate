from pydantic import BaseModel
from app.schemas import trip_schema,payment_schema,user_schema

class TripBookBase(BaseModel):
    trip_id:int
    driver_id:int
    passenger_id:int
    booking_status:str
    payable_amount:int
    seat_count:int

    
class CreateNewBooking(BaseModel):
    trip_id:int
    driver_id:int
    passenger_id:int
    payable_amount:int
    seat_count:int

class CreatedBooking(BaseModel):
    booking_id:int
    booking_status:str

class CancelledBooking(CreatedBooking):
    pass
    
class PassangerBookingList(TripBookBase):
    booking_id:int
    trip:trip_schema.TripDetailBase

class BookingDetail(BaseModel):
    user:user_schema.GetUser
    booking_details:TripBookBase
    payment_details:payment_schema.PaymentDetail
    trip:trip_schema.TripDetailBase
