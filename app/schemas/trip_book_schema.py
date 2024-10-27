from pydantic import BaseModel
from app.schemas import trip_schema

class TripBookBase(BaseModel):
    trip_id:int
    driver_id:int
    passanger_id:int
    booking_status:str
    payable_amount:int
    seat_count:int

class CreateNewBooking(BaseModel):
    trip_id:int
    driver_id:int
    passenger_id:int
    payable_amount:int
    seat_count:int

class PassangerBookingList(BaseModel):
    booking_id:int
    trip:trip_schema.TripList