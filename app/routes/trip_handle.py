from fastapi import APIRouter,Depends,Form
from app import database,oauth2,errors,models,enums
from sqlalchemy import func
from app.schemas import trip_schema,trip_book_schema,user_schema,vehicle_schema,base_schema
from sqlalchemy.orm import Session,joinedload
from typing import List,Union
from datetime import datetime,date
from sqlalchemy import cast,Date
from sqlalchemy import or_
from datetime import datetime,timezone


route = APIRouter(prefix='/trip')


@route.post('',response_model=base_schema.BaseSchema)
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
        return errors.NotAuthorizedException

    userCheck = db.query(models.UserIdProof).filter(models.UserIdProof.user_id==current_user.user_id).first()
    if not userCheck:
        return errors.DriverNotEligibleException
    
    vehicleCheck = db.query(models.Vehicle).filter(models.Vehicle.user_id==current_user.user_id,
                                                      models.Vehicle.vehicle_id==vehicle_id).first()
    if (vehicleCheck is None):
        return errors.NoVehicleException

    if (seats_available > vehicleCheck.seat_capacity or seats_available<1):
        return errors.InvalidSeatCapacityException
    
    if start_time <= datetime.now() or end_time <= start_time:
        return errors.InvalidDateTimeException
    

    trip = trip_schema.CreateTrip(vehicle_id=vehicle_id,
                                    source_address_line=source_address_line.strip().capitalize(),
                                    source_city=source_city.strip().capitalize(),
                                    source_state=source_state.strip().capitalize(),
                                    source_country=source_country.strip().capitalize(),
                                    source_pincode=source_pincode,
                                    destination_address_line=destination_address_line.strip().capitalize(),
                                    destination_city=destination_city.strip().capitalize(),
                                    destination_state=destination_state.strip().capitalize(),
                                    destination_country=destination_country.strip().capitalize(),
                                    destination_pincode=destination_pincode,
                                    seats_available=seats_available,
                                    fees_per_person=fees_per_person,
                                    start_time=start_time,
                                    end_time=end_time)
    
    new_trip = models.Trip(user_id=current_user.user_id,**dict(trip))
    db.add(new_trip)
    db.commit()
    
    context = base_schema.BaseSchema

    return context

@route.put('/',response_model=base_schema.BaseSchema)
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
        return errors.NoTripException
    
    if trip.first().user_id is not current_user.user_id:
        return errors.NotAuthorizedException
    
    vehicleCheck = db.query(models.Vehicle).filter(models.Vehicle.user_id==current_user.user_id,
                                                      models.Vehicle.vehicle_id==vehicle_id).first()
    if (vehicleCheck is None):
        return errors.NoVehicleException

    if (seats_available > vehicleCheck.seat_capacity-1 or seats_available<1):
        return errors.InvalidSeatCapacityException
    
    if start_time < datetime.now() or end_time < start_time:
        return errors.InvalidDateTimeException
    
    edit_trip = trip_schema.EditTrip(vehicle_id=vehicle_id,
                                    source_address_line=source_address_line.strip().capitalize(),
                                    source_city=source_city.strip().capitalize(),
                                    source_state=source_state.strip().capitalize(),
                                    source_country=source_country.strip().capitalize(),
                                    source_pincode=source_pincode,
                                    destination_address_line=destination_address_line.strip().capitalize(),
                                    destination_city=destination_city.strip().capitalize(),
                                    destination_state=destination_state.strip().capitalize(),
                                    destination_country=destination_country.strip().capitalize(),
                                    destination_pincode=destination_pincode,
                                    seats_available=seats_available,
                                    fees_per_person=fees_per_person,
                                    status=status,
                                    start_time=start_time,
                                    end_time=end_time)
    
    trip.update(dict(edit_trip))
    db.commit()

    context = base_schema.BaseSchema
    return context

@route.get('/search',response_model=trip_schema.TripListResponse)
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
                                            models.Trip.driver != current_user,models.Trip.seats_available>0)

    if start_date:
        trips = trips.filter(cast(models.Trip.start_time, Date) >= start_date).all()
    else:
        trips = trips.all()

    if len(trips) < 1:
        return errors.NoTripException
    
    trip_list = []
    for trip in trips:
        t = trip_schema.TripList.model_validate(trip)
        t.driver_name=trip.driver.name
        t.vehicle_type=trip.vehicle.type
        trip_list.append(t)

    context = {'data':trip_list}
    return context

@route.get('',response_model=trip_schema.TripListResponse)
def get_trips(db:Session = Depends(database.get_db),
              current_user:models.User = Depends(oauth2.get_current_user),
              current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)
              ,limit:int = 10):

    if current_user_type == enums.UserType.DRIVER:
        trips = db.query(models.Trip).filter(models.Trip.user_id==current_user.user_id).order_by('start_time').all()
    else:
        return errors.NotAuthorizedException

    if len(trips)==0:
        return errors.NoTripException
    
    trip_list = []
    for trip in trips:
        t = trip_schema.TripList.model_validate(trip)
        t.driver_name=trip.driver.name
        t.vehicle_type=trip.vehicle.type
        trip_list.append(t)

    context = {'data':trip_list}
    return context

@route.get('/',response_model=trip_schema.TripDetailResponse)
def get_trip_detail(trip_id:int,
                    db:Session=Depends(database.get_db),
                    current_user:models.User = Depends(oauth2.get_current_user),
                    current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):

    context = {}

    if current_user_type == enums.UserType.DRIVER:
        trip = (db.query(models.Trip)
                .filter(models.Trip.trip_id==trip_id,models.Trip.user_id==current_user.user_id)
                .first())
        
        if trip is None:
            return errors.NoTripException
        get_bookings = db.query(models.TripBook).filter(models.TripBook.trip_id==trip_id,models.TripBook.driver_id==current_user.user_id).all()
        passengers = []

        for i in get_bookings:
            passengers.append(user_schema.PassengerDetailBase(booking_id=i.booking_id,
                                                             name=i.passenger.name,
                                                             seat_count = i.seat_count,
                                                             payable_amount = i.payable_amount,
                                                             ))

        passenger_count = len(passengers)

        context.update({"passenger_count":passenger_count,"passenger_list":passengers})

    elif current_user_type == enums.UserType.PASSENGER:
        trip = (db.query(models.Trip)
                .filter(models.Trip.trip_id==trip_id)
                .first())
        
        if trip is None:
            return errors.NoTripException
        
        driver = user_schema.DriverDetailBase(user_id=trip.driver.user_id,
                                        name=trip.driver.name,
                                        email=trip.driver.email,
                                        contact_no=trip.driver.contact_no,
                                        profile_photo=trip.driver.profile_photo,
                                        ratings=trip.driver.ratings,
                                        rating_count=trip.driver.rating_count)
        context.update({"driver":driver})
    else:
        return errors.InvalidUserTypeException
    
    trip_detail = trip_schema.TripBase.model_validate(trip)

    vehicle = vehicle_schema.VehicleBase(vehicle_id=trip.vehicle.vehicle_id,
                                            type =trip.vehicle.type,
                                            model =trip.vehicle.model,
                                            seat_capacity =trip.vehicle.seat_capacity,
                                            registration_number =trip.vehicle.registration_number)
    vehicle_images = [image[0] for image in db.query(models.VehicleImage.image_path).filter(models.VehicleImage.vehicle_id==trip.vehicle_id).all() ]

    context.update({"vehicle":vehicle,"vehicle_images":vehicle_images,"trip":trip_detail})

    context = {'data':context}

    return context

@route.get('/history',response_model=trip_schema.TripHistoryListResponse)
def get_trip_history(current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                        db:Session=Depends(database.get_db)):
    trip_list = []

    if current_user_type == enums.UserType.DRIVER:
        count_passanger = (db.query(models.TripBook.trip_id,
                                    func.count(models.TripBook.booking_id).label('no_of_passangers'))
                                    .group_by(models.TripBook.booking_id).subquery())

        trips = reversed(db.query(models.Trip,func.coalesce(count_passanger.c.no_of_passangers,0).label('no_of_passangers'))
                        .outerjoin(count_passanger, models.Trip.trip_id==count_passanger.c.trip_id)
                        .group_by(models.Trip.trip_id,count_passanger.c.no_of_passangers)
                        .filter(or_(models.Trip.status==enums.TripStatus.COMPLETED,
                                    models.Trip.status==enums.TripStatus.CANCELLED),
                                    models.Trip.user_id==current_user.user_id)
                        .order_by(models.Trip.end_time)
                        .all())    

        for trip in trips:
            t = trip_schema.DriverTripHistoryList.model_validate(trip[0])
            t.no_of_passangers=trip[1]
            trip_list.append(t)


    elif current_user_type == enums.UserType.PASSENGER:
        trips = (db.query(models.TripBook).filter(models.TripBook.passenger_id==current_user.user_id,
                                                 or_(models.Trip.status==enums.TripStatus.COMPLETED,
                                                    models.Trip.status==enums.TripStatus.CANCELLED))
                                                    .all())

        trip_list = [trip_schema.PassengerTripHistoryList.model_validate(trip) for trip in trips]

    if len(trip_list) < 1:
        return errors.NoTripException


    context = {'data':trip_list}
    return context

@route.put('/start_trip',response_model=base_schema.BaseSchema)
def start_trip(trip_id:int,
                  current_user:models.User=Depends(oauth2.get_current_user),
                  current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                  db:Session=Depends(database.get_db)):
    
    if current_user_type != enums.UserType.DRIVER:
        return errors.NotAuthorizedException
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id,
                                        models.Trip.user_id==current_user.user_id,
                                        models.Trip.status==enums.TripStatus.UPCOMING).first()
    

    if not trip:
        return errors.NoTripException
    
    
    
    trip.status = enums.TripStatus.ONGOING.value

    db.commit()
    
    context = base_schema.BaseSchema

    return context

@route.put('/cancel_trip',response_model=base_schema.BaseSchema)
def cancel_trip(trip_id:int,
                  current_user:models.User=Depends(oauth2.get_current_user),
                  current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                  db:Session=Depends(database.get_db)):
    
    if current_user_type != enums.UserType.DRIVER:
        return errors.NotAuthorizedException
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id,
                                        models.Trip.user_id==current_user.user_id,
                                        models.Trip.status==enums.TripStatus.UPCOMING).first()
    
    if datetime.now(timezone.utc) >= trip.start_time:
        return errors.InvalidActionException

    booking = db.query(models.TripBook).filter(models.TripBook.trip_id==trip.trip_id,
                                               models.TripBook.booking_status==enums.BookingStatus.CONFIRMED).all()

    if not trip:
        return errors.NoTripException
    
    if len(booking) > 0:
        for i in booking:
            payment = db.query(models.Payment).filter(models.Payment.booking_id==i.booking_id,models.Payment.payment_status==enums.PaymentStatus.PENDING).first()
            if payment:
                i.booking_status = enums.BookingStatus.CANCELLED.value
                payment.payment_status = enums.PaymentStatus.RETURNED.value

    trip.status = enums.TripStatus.CANCELLED.value

    db.commit()
    
    context = base_schema.BaseSchema

    return context

@route.put('/complete_trip',response_model=base_schema.BaseSchema)
def complete_trip(trip_id:int,
                  current_user:models.User=Depends(oauth2.get_current_user),
                  current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                  db:Session=Depends(database.get_db)):
    
    if current_user_type != enums.UserType.DRIVER:
        return errors.NotAuthorizedException
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id,
                                        models.Trip.user_id==current_user.user_id,
                                        or_(models.Trip.status==enums.TripStatus.UPCOMING,
                                        models.Trip.status==enums.TripStatus.ONGOING)).first()
    
    if not trip:
        return errors.NoTripException
    
    if trip.start_time<datetime.now(timezone.utc):
        return errors.InvalidActionException
    
    booking = db.query(models.TripBook).filter(models.TripBook.trip_id==trip.trip_id,
                                               models.TripBook.booking_status==enums.BookingStatus.CONFIRMED).all()

    
    
    if len(booking) > 0:
        for i in booking:
            payment = db.query(models.Payment).filter(models.Payment.booking_id==i.booking_id,models.Payment.payment_status==enums.PaymentStatus.PENDING).first()
            if payment:
                payment.payment_status = enums.PaymentStatus.SUCCESS.value

    
    
    trip.status = enums.TripStatus.COMPLETED.value

    db.commit()
    
    context = base_schema.BaseSchema

    return context