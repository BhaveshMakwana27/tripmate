from pydantic import BaseModel
from datetime import datetime,timedelta
from typing import List
from app.schemas import user_schema,vehicle_schema


class TripBase(BaseModel):
    vehicle_id:int
    source_address_line:str
    source_city:str
    source_state:str
    source_country:str
    source_pincode:str
    destination_address_line:str
    destination_city:str
    destination_state:str
    destination_country:str
    destination_pincode:str
    seats_available:int
    fees_per_person:int
    status:str
    start_time:datetime
    end_time:datetime
    duration:timedelta
    

class TripDetailBase(BaseModel):
    trip_id : int
    source_address_line:str
    source_city:str
    source_state:str
    source_country:str
    source_pincode:str
    destination_address_line:str
    destination_city:str
    destination_state:str
    destination_country:str
    destination_pincode:str
    start_time : datetime
    end_time : datetime
    fees_per_person : int

class CreateTrip(BaseModel):
    vehicle_id:int
    source_address_line:str
    source_city:str
    source_state:str
    source_country:str
    source_pincode:str
    destination_address_line:str
    destination_city:str
    destination_state:str
    destination_country:str
    destination_pincode:str
    seats_available:int
    fees_per_person:int
    start_time:datetime
    end_time:datetime


class EditTrip(TripBase):
    pass


class TripDetailPassenger(BaseModel):
    trip:TripBase
    driver:user_schema.DriverDetailBase
    vehicle:vehicle_schema.VehicleBase
    vehicle_images:List[str]


class TripDetailDriver(BaseModel):
    trip:TripBase
    vehicle:vehicle_schema.VehicleBase
    vehicle_images:List[str]
    passenger_count:int
    passenger_list:List[user_schema.PassengerDetailBase]


class TripList(BaseModel):
    trip_id:int
    source_city:str
    destination_city:str
    status:str
    seats_available:int
    start_time:datetime
    end_time:datetime
    vehicle:vehicle_schema.VehicleType
    driver:user_schema.DriverBase

class TripHistoryList(BaseModel):
    trip_id:int
    source_city:str
    destination_city:str
    status:str
    start_time:datetime
    end_time:datetime
    
class DriverTripHistory(BaseModel):
    Trip:TripHistoryList
    no_of_passangers:int

class PassengerTripHistory(BaseModel):
    trip_id:int
    source_city:str
    destination_city:str
    status:str
    start_time:datetime
    end_time:datetime
