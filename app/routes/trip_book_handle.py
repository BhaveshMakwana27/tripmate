from fastapi import APIRouter,Depends,Form
from app import database,oauth2,models,errors,enums
from app.schemas import trip_book_schema,payment_schema,trip_schema,user_schema
from app.config import settings
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func,or_
from typing import List


route = APIRouter(prefix="/trip_book")

@route.post("",response_model=trip_book_schema.CreatedBooking)
def book_trip(trip_id:int=Form(...),
              seat_count:int=Form(...),
              payment_method:enums.PaymentMethod=Form(enums.PaymentMethod.CASH),
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

    if payment_method!=enums.PaymentMethod.CASH and payment_method!=enums.PaymentMethod.ONLINE:
        raise errors.InvalidPaymentMethod
    
    new_booking = trip_book_schema.CreateNewBooking(trip_id=trip_id,
                                  driver_id=driver_id,
                                  passenger_id=passenger_id,
                                  payable_amount=payable_amount,
                                  seat_count=seat_count,
                                  )
    
    new_booking = models.TripBook(**dict(new_booking))
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    new_payment = models.Payment(booking_id=new_booking.booking_id,
                                 amount=payable_amount)
    
    if payment_method==enums.PaymentMethod.ONLINE:
        new_payment.payment_method=payment_method
        new_payment.payment_status=enums.PaymentStatus.SUCCESS.value

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    if not db.query(models.TripBook).filter(models.TripBook.booking_id==new_booking.booking_id).first():
        raise errors.BookingFailedException
    
    trip.seats_available-=new_booking.seat_count
    db.commit()

    booking = trip_book_schema.CreatedBooking(booking_id=new_booking.booking_id
                                             ,booking_status=new_booking.booking_status)
    
    return booking

@route.get('',response_model=List[trip_book_schema.PassangerBookingList])
def get_booking_list(db:Session = Depends(database.get_db),                 
                 current_user:models.User = Depends(oauth2.get_current_user),
                 current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):
    
    if current_user_type == enums.UserType.PASSENGER:
        bookings = (db.query(models.TripBook).join(models.Trip)
                        .filter(models.TripBook.passenger_id==current_user.user_id,
                                or_(models.Trip.status==enums.TripStatus.UPCOMING,
                                models.Trip.status==enums.TripStatus.ONGOING)
                                ,models.TripBook.booking_status==enums.BookingStatus.CONFIRMED)
                        .order_by(models.TripBook.booking_time)
                    .all())
    
    if len(bookings)<1:
        raise errors.NoCurrentBookings
    
    return bookings

@route.get('/cancel_booking',response_model=trip_book_schema.CancelledBooking)
def cancel_booking(booking_id:int=Form(...),
                   current_user=models.User,
                   current_user_type:enums.BookingStatus=Depends(oauth2.get_current_user_type),
                   db:Session=Depends(database.get_db)):
    
    if current_user_type == enums.UserType.DRIVER.value:
        raise errors.InvalidUserTypeException

    get_booking = (db.query(models.TripBook).filter(models.TripBook.booking_id==booking_id,
                                                   models.TripBook.passenger_id==current_user.user_id)
                                                   .first())
    get_payment = (db.query(models.Payment).filter(models.Payment.booking_id==booking_id).first())
    
    if not get_booking:
        raise errors.NoCurrentBookings
    
    if get_booking.booking_status == enums.BookingStatus.CANCELLED:
        raise errors.BookingAlreadyCancelledException
    
    trip = (db.query(models.Trip).filter(models.Trip.trip_id==get_booking.trip_id,models.Trip.user_id!=current_user.user_id).first())

    if not trip:
        raise errors.NoTripException
    
    if trip.status != enums.TripStatus.UPCOMING:
        raise errors.InvalidCancellationException

    get_booking.booking_status = enums.BookingStatus.CANCELLED.value
    trip.seats_available += get_booking.seat_count
    get_payment.payment_status=enums.PaymentStatus.RETURNED.value

    db.commit()
    db.refresh(get_booking)
    db.refresh(get_payment)
    booking = trip_book_schema.CancelledBooking(booking_id=get_booking.booking_id,
                                                booking_status=get_booking.booking_status)

    return booking

@route.get('/',response_model=trip_book_schema.BookingDetail)
def get_booking_details(booking_id:int,
                        current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                        db:Session=Depends(database.get_db)):
    
    booking = db.query(models.TripBook).filter(models.TripBook.booking_id==booking_id).first()

    if not booking:
        raise errors.NoCurrentBookings
    
    payment = db.query(models.Payment).filter(models.Payment.booking_id==booking_id).first()
    trip = db.query(models.Trip).filter(models.Trip.trip_id==booking.trip_id).first()

    if current_user_type == enums.UserType.DRIVER:
        if booking.driver_id != current_user.user_id:
            raise errors.NotAuthorizedException
        user = db.query(models.User).filter(models.User.user_id==booking.passenger_id).first()
    elif current_user_type == enums.UserType.PASSENGER:
        if booking.passenger_id != current_user.user_id:
            raise errors.NotAuthorizedException
        user = db.query(models.User).filter(models.User.user_id==trip.user_id).first()

    user = user_schema.GetUser(user_id=user.user_id,
                                name=user.name,
                                contact_no=user.contact_no,
                                email=user.email,
                                profile_photo=user.profile_photo)

    trip = trip_schema.TripDetailBase(trip_id=trip.trip_id,
                                        source_address_line=trip.source_address_line,
                                        source_city=trip.source_city,
                                        source_state=trip.source_state,
                                        source_country=trip.source_country,
                                        source_pincode=trip.source_pincode,
                                        destination_address_line=trip.destination_address_line,
                                        destination_city=trip.destination_city,
                                        destination_state=trip.destination_state,
                                        destination_country=trip.destination_country,
                                        destination_pincode=trip.destination_pincode,
                                        start_time =trip.start_time,
                                        end_time =trip.end_time,
                                        fees_per_person = trip.fees_per_person)
    
    booking = trip_book_schema.TripBookBase(trip_id=booking.trip_id,
                                                 driver_id=booking.driver_id,
                                                 passenger_id=booking.passenger_id,
                                                 booking_status=booking.booking_status,
                                                 seat_count=booking.seat_count,
                                                 payable_amount=booking.payable_amount)
    
    payment = payment_schema.PaymentDetail(payment_id=payment.payment_id,
                                           booking_id=payment.booking_id,
                                           payment_method=payment.payment_method,
                                           payment_status=payment.payment_status)


    context = {"booking_details":booking,"payment_details":payment, "trip":trip, "user":user}
    return context

@route.get('/history',response_model=List[trip_book_schema.PassangerBookingList])
def get_booking_history(current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                        db:Session=Depends(database.get_db)):
    
    if current_user_type != enums.UserType.PASSENGER:
        raise errors.NotAuthorizedException
    
    booking = (db.query(models.TripBook).join(models.Trip).filter(models.TripBook.passenger_id==current_user.user_id,
                                               or_(models.TripBook.booking_status==enums.BookingStatus.CANCELLED,
                                                   models.TripBook.booking_status==enums.BookingStatus.CONFIRMED))
                                                   .order_by(models.TripBook.booking_time)
                                                   .all())
    
    if len(booking) < 1:
        raise errors.NoCurrentBookings
    return booking

