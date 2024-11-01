from fastapi import APIRouter,Depends,Form
from app import database,oauth2,errors,models,enums
from sqlalchemy import func
from app.schemas import trip_schema
from sqlalchemy.orm import Session,joinedload
from typing import List
from datetime import datetime,date
from sqlalchemy import cast,Date


route = APIRouter(prefix='/trip')


@route.post('')
def post_trip(vehicle_id:int = Form(...),
            source_address_line:str = Form(...),
            source_city:str = Form(...),
            source_state:str = Form(...),
            source_country:str = Form("India"),
            source_pincode:str = Form(...),
            destination_address_line:str = Form(...),
            destination_city:str = Form(...),
            destination_state:str = Form(...),
            destination_country:str = Form("India"),
            destination_pincode:str = Form(...),
            seats_available:int = Form(...),
            fees_per_person:int = Form(...),
            start_time:datetime = Form(...),
            end_time:datetime = Form(...),
            db:Session = Depends(database.get_db),
            current_user:models.User = Depends(oauth2.get_current_user),
            current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)
           ):

    if current_user_type is not enums.UserType.DRIVER:
        raise errors.NotAuthorizedException

    userCheck = db.query(models.UserIdProof).filter(models.UserIdProof.user_id==current_user.user_id).first()
    if not userCheck:
        raise errors.DriverNotEligibleException
    
    vehicleCheck = db.query(models.Vehicle).filter(models.Vehicle.user_id==current_user.user_id,
                                                      models.Vehicle.vehicle_id==vehicle_id).first()
    if (vehicleCheck is None):
        raise errors.NoVehicleException

    if (seats_available > vehicleCheck.seat_capacity-1 or seats_available<1):
        raise errors.InvalidSeatCapacityException
    
    if start_time <= datetime.now() or end_time <= start_time:
        raise errors.InvalidDateTimeException
    

    trip = trip_schema.CreateTrip(vehicle_id=vehicle_id,
                                    source_address_line=source_address_line.capitalize(),
                                    source_city=source_city.capitalize(),
                                    source_state=source_state.capitalize(),
                                    source_country=source_country.capitalize(),
                                    source_pincode=source_pincode,
                                    destination_address_line=destination_address_line.capitalize(),
                                    destination_city=destination_city.capitalize(),
                                    destination_state=destination_state.capitalize(),
                                    destination_country=destination_country.capitalize(),
                                    destination_pincode=destination_pincode,
                                    seats_available=seats_available,
                                    fees_per_person=fees_per_person,
                                    start_time=start_time,
                                    end_time=end_time)
    
    new_trip = models.Trip(user_id=current_user.user_id,**dict(trip))
    db.add(new_trip)
    db.commit()
    
    return True

@route.get('/request_edit/{trip_id}',response_model=trip_schema.TripBase)
def request_trip_edit(trip_id:int,db:Session=Depends(database.get_db),
                      current_user:models.User = Depends(oauth2.get_current_user),
                      current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):

    if current_user_type != enums.UserType.DRIVER:
        raise errors.NotAuthorizedException

    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id,models.Trip.user_id==current_user.user_id)
    if not trip.first():
        raise errors.NoTripException

    return trip.first()

@route.put('')
def edit_trip(trip_id:int,
            vehicle_id:int = Form(...),
            source_address_line:str = Form(...),
            source_city:str = Form(...),
            source_state:str = Form(...),
            source_country:str = Form(...),
            source_pincode:str = Form(...),
            destination_address_line:str = Form(...),
            destination_city:str = Form(...),
            destination_state:str = Form(...),
            destination_country:str = Form(...),
            destination_pincode:str = Form(...),
            seats_available:int = Form(...),
            fees_per_person:int = Form(...),
            status:str = Form(...),
            start_time:datetime = Form(...),
            end_time:datetime = Form(...),
            db:Session = Depends(database.get_db),
            current_user:models.User = Depends(oauth2.get_current_user)):
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id)
    if not trip.first():
        raise errors.NoTripException
    
    if trip.first().user_id is not current_user.user_id:
        raise errors.NotAuthorizedException
    
    vehicleCheck = db.query(models.Vehicle).filter(models.Vehicle.user_id==current_user.user_id,
                                                      models.Vehicle.vehicle_id==vehicle_id).first()
    if (vehicleCheck is None):
        raise errors.NoVehicleException

    if (seats_available > vehicleCheck.seat_capacity-1 or seats_available<1):
        raise errors.InvalidSeatCapacityException
    
    if start_time < datetime.now() or end_time < start_time:
        raise errors.InvalidDateTimeException
    
    edit_trip = trip_schema.EditTrip(vehicle_id=vehicle_id,
                                    source_address_line=source_address_line,
                                    source_city=source_city,
                                    source_state=source_state,
                                    source_country=source_country,
                                    source_pincode=source_pincode,
                                    destination_address_line=destination_address_line,
                                    destination_city=destination_city,
                                    destination_state=destination_state,
                                    destination_country=destination_country,
                                    destination_pincode=destination_pincode,
                                    seats_available=seats_available,
                                    fees_per_person=fees_per_person,
                                    status=status,
                                    start_time=start_time,
                                    end_time=end_time)
    
    trip.update(dict(edit_trip))
    db.commit()
    return True

@route.get('/search',response_model=List[trip_schema.TripList])
def search_trip(source_city:str = Form("*"),
                destination_city:str = Form("*"),
                start_date:date = Form(None),
                db:Session = Depends(database.get_db),
                current_user:models.User = Depends(oauth2.get_current_user),
                current_user_type:models.User = Depends(oauth2.get_current_user_type)):
    

    if current_user_type == enums.UserType.DRIVER:
        trips = db.query(models.Trip).filter(models.Trip.source_city.contains(source_city),
                                            models.Trip.destination_city.contains(destination_city),
                                            models.Trip.driver == current_user)

    elif current_user_type == enums.UserType.PASSENGER:
        trips = db.query(models.Trip).filter(models.Trip.source_city.contains(source_city),
                                            models.Trip.destination_city.contains(destination_city),
                                            models.Trip.driver != current_user)

    if not start_date:
        trips = trips.all()
        return trips

    trips = trips.filter(cast(models.Trip.start_time, Date) >= start_date).all()

    if len(trips) < 1:
        raise errors.NoTripException
    
    return trips

@route.get('',response_model=List[trip_schema.TripList])
def get_trips(db:Session = Depends(database.get_db),
              current_user:models.User = Depends(oauth2.get_current_user),
              current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)
              ,limit:int = 10):

    if current_user_type == enums.UserType.DRIVER:
        trips = db.query(models.Trip).filter(models.Trip.user_id==current_user.user_id).order_by('start_time').all()
    else:
        raise errors.NotAuthorizedException

    if len(trips)==0:
        raise errors.NoTripException

    return trips

@route.get('/',response_model=trip_schema.TripDetail)
def get_trip_detail(trip_id:int,
                    db:Session=Depends(database.get_db),
                    current_user:models.User = Depends(oauth2.get_current_user),
                    current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):

    trip = (db.query(models.Trip)
              .filter(models.Trip.trip_id==trip_id)
              .first())
    if trip is None:
        raise errors.NoTripException
    
    
    images =[image[0] for image in db.query(models.VehicleImage.image_path).filter(models.VehicleImage.vehicle_id==trip.vehicle_id).all() ]

    return trip,{'vehicle_images':images}

@route.get('/history',response_model=List[trip_schema.DriverTripHistory])
def get_trip_history(current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                        db:Session=Depends(database.get_db)):

    if current_user_type == enums.UserType.DRIVER:
        count_passanger = (db.query(models.TripBook.trip_id,
                                    func.count(models.TripBook.booking_id).label('no_of_passangers'))
                                    .group_by(models.TripBook.booking_id).subquery())
        
        trips = reversed(db.query(models.Trip,func.coalesce(count_passanger.c.no_of_passangers,0).label('no_of_passangers'))
                        .outerjoin(count_passanger, models.Trip.trip_id==count_passanger.c.trip_id)
                        .group_by(models.Trip.trip_id,count_passanger.c.no_of_passangers)
                        .filter(models.Trip.user_id==current_user.user_id)
                        .order_by(models.Trip.end_time)
                        .all())
        return trips
    
    if current_user_type == enums.UserType.PASSENGER:
        
        trips = db.query(models.TripBook).filter(models.TripBook.passenger_id==current_user.user_id).all()
        return trips
    
    return True

@route.get('/history_detail')
def get_trip_history_detail():
    return True
