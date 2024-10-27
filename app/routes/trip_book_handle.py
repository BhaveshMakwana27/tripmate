from fastapi import APIRouter,Depends,Form
from app import database,oauth2,models,errors,enums
from app.schemas import trip_book_schema
from app.config import settings
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func
from typing import List


route = APIRouter(prefix="/trip_book")

@route.post("/")
def book_trip(trip_id:int=Form(...),
              seat_count:int=Form(...),
                db:Session = Depends(database.get_db),
                current_user:models.User = Depends(oauth2.get_current_user),
                current_user_type:models.User = Depends(oauth2.get_current_user_type)):
    
    if current_user_type != enums.UserType.PASSENGER:
        raise errors.NotAuthorizedException
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id).first()
    if trip is None:
        raise errors.NoTripException
    
    isBooked = db.query(models.TripBook).filter(models.TripBook.passenger_id==current_user.user_id,models.TripBook.trip_id==trip_id).first()
    if isBooked:
        raise errors.AlreadyBookedException

    driver_id = trip.user_id
    passenger_id = current_user.user_id

    if driver_id==passenger_id:
        raise errors.InvalidBookingException
    
    if seat_count>trip.seats_available or seat_count<1:
        raise errors.InvalidSeatCapacityException
    
    payable_amount = trip.fees_per_person * seat_count

    new_booking = trip_book_schema.CreateNewBooking(trip_id=trip_id,
                                  driver_id=driver_id,
                                  passenger_id=passenger_id,
                                  payable_amount=payable_amount,
                                  seat_count=seat_count)
    
    new_booking = models.TripBook(**dict(new_booking))
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    if not db.query(models.TripBook).filter(models.TripBook.booking_id==new_booking.booking_id).first():
        raise errors.BookingFailedException
    
    trip.seats_available-=new_booking.seat_count
    db.commit()

    return new_booking

@route.get('',response_model=List[trip_book_schema.PassangerBookingList])
def get_booking_list(db:Session = Depends(database.get_db),                 
                 current_user:models.User = Depends(oauth2.get_current_user),
                 current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):
    bookings = (db.query(models.TripBook)
                    .filter(models.TripBook.passenger_id==current_user.user_id)
                    .order_by(models.TripBook.booking_time)
                    .all())
    
    if len(bookings)<1:
        raise errors.NoCurrentBookings
    
    return bookings

@route.post('/payment')
def make_payment(booking_id:int,current_user:models.User=Depends(oauth2.get_current_user),
                 current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                 db:Session=Depends(database.get_db)):
    
    check_booking = db.query(models.TripBook).filter(models.TripBook.booking_id==booking_id).first()
    if not check_booking:
        raise errors.NoCurrentBookings
    
    if check_booking.passenger_id != current_user or current_user_type != enums.UserType.PASSENGER:
        raise errors.NotAuthorizedException
    
    pass