from pydantic import BaseModel,ConfigDict
from datetime import datetime,timedelta
from typing import List,Union
from app.schemas import user_schema,vehicle_schema,base_schema,trip_schema

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

    model_config = ConfigDict(from_attributes=True)
    
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
    status : str

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

class TripDetailDriver(BaseModel):
    trip:TripBase
    vehicle:vehicle_schema.VehicleBase
    vehicle_images:List[str]
    passenger_count:int
    passenger_list:List[user_schema.PassengerDetailBase]

    model_config = ConfigDict(from_attributes=True)

class TripDetailResponse(base_schema.BaseSchema):
    data : Union[trip_schema.TripDetailDriver,trip_schema.TripDetailPassenger]


class TripList(BaseModel):
    trip_id:int
    source_city:str
    destination_city:str
    status:str
    seats_available:int
    start_time:datetime
    end_time:datetime
    vehicle_type:str = None
    driver_name:str = None

    model_config = ConfigDict(from_attributes=True)

class TripListResponse(base_schema.BaseSchema):
    data : List[TripList]


class TripHistoryList(BaseModel):
    trip_id:int
    source_city:str
    destination_city:str
    status:str
    start_time:datetime
    end_time:datetime
    
class DriverTripHistoryList(TripHistoryList):
    no_of_passangers:int = 0

    model_config = ConfigDict(from_attributes=True)

class PassengerTripHistoryList(TripHistoryList):
    model_config = ConfigDict(from_attributes=True)
    pass

class TripHistoryListResponse(base_schema.BaseSchema):
    data : List[Union[trip_schema.PassengerTripHistoryList,trip_schema.DriverTripHistoryList]]