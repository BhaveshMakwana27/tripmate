from fastapi import APIRouter,Depends,Form
from app import database,oauth2,models,errors,enums
from app.schemas import trip_book_schema,payment_schema,trip_schema,user_schema
from app.config import settings
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func,or_
from typing import List


route = APIRouter(prefix="/trip_book")

@route.post("",response_model=trip_book_schema.BookingStatusResponse)
def book_trip(trip_id:int=Form(...),
              seat_count:int=Form(...),
              payment_method:enums.PaymentMethod=Form(enums.PaymentMethod.CASH),
                db:Session = Depends(database.get_db),
                current_user:models.User = Depends(oauth2.get_current_user),
                current_user_type:models.User = Depends(oauth2.get_current_user_type)):
    
    if current_user_type != enums.UserType.PASSENGER:
        return errors.NotAuthorizedException
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id).first()
    if trip is None:
        return errors.NoTripException
    
    isBooked = db.query(models.TripBook).filter(models.TripBook.passenger_id==current_user.user_id,models.TripBook.trip_id==trip_id).first()
    if isBooked:
        return errors.AlreadyBookedException

    driver_id = trip.user_id
    passenger_id = current_user.user_id

    if driver_id==passenger_id:
        return errors.InvalidBookingException
    
    if seat_count>trip.seats_available or seat_count<1:
        return errors.InvalidSeatCapacityException
    
    payable_amount = trip.fees_per_person * seat_count

    if payment_method!=enums.PaymentMethod.CASH and payment_method!=enums.PaymentMethod.ONLINE:
        return errors.InvalidPaymentMethod
    
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
        return errors.BookingFailedException
    
    trip.seats_available-=new_booking.seat_count
    db.commit()

    booking = trip_book_schema.BookingStatus(booking_id=new_booking.booking_id,
                                             booking_status=new_booking.booking_status)
    
    context = trip_book_schema.BookingStatusResponse(data=booking)
    
    
    return context

@route.get('',response_model=trip_book_schema.PassangerBookingListResponse)
def get_booking_list(db:Session = Depends(database.get_db),                 
                 current_user:models.User = Depends(oauth2.get_current_user),
                 current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):
    

    if current_user_type != enums.UserType.PASSENGER:
        return errors.InvalidUserTypeException
    bookings = (db.query(models.TripBook).join(models.Trip)
                    .filter(models.TripBook.passenger_id==current_user.user_id,
                            or_(models.Trip.status==enums.TripStatus.UPCOMING,
                            models.Trip.status==enums.TripStatus.ONGOING)
                            ,models.TripBook.booking_status==enums.BookingStatus.CONFIRMED)
                    .order_by(models.TripBook.booking_time)
                .all())
    
    if len(bookings)<1:
        return errors.NoCurrentBookings
    
    booking_list = []
    for booking in bookings:
        b = trip_book_schema.PassangerBookingList.model_validate(booking)
        b.driver_name = booking.driver.name
        b.trip = trip_schema.TripDetailBase.model_validate(booking.trip)
        booking_list.append(b)

    context = trip_book_schema.PassangerBookingListResponse(data=booking_list)
    return context

@route.get('/cancel_booking',response_model=trip_book_schema.BookingStatusResponse)
def cancel_booking(booking_id:int=Form(...),
                   current_user=models.User,
                   current_user_type:enums.BookingStatus=Depends(oauth2.get_current_user_type),
                   db:Session=Depends(database.get_db)):
    
    if current_user_type == enums.UserType.DRIVER.value:
        return errors.InvalidUserTypeException

    get_booking = (db.query(models.TripBook).filter(models.TripBook.booking_id==booking_id,
                                                   models.TripBook.passenger_id==current_user.user_id)
                                                   .first())
    get_payment = (db.query(models.Payment).filter(models.Payment.booking_id==booking_id).first())
    
    if not get_booking:
        return errors.NoCurrentBookings
    
    if get_booking.booking_status == enums.BookingStatus.CANCELLED:
        return errors.BookingAlreadyCancelledException
    
    trip = (db.query(models.Trip).filter(models.Trip.trip_id==get_booking.trip_id,models.Trip.user_id!=current_user.user_id).first())

    if not trip:
        return errors.NoTripException
    
    if trip.status != enums.TripStatus.UPCOMING:
        return errors.InvalidCancellationException

    get_booking.booking_status = enums.BookingStatus.CANCELLED.value
    trip.seats_available += get_booking.seat_count
    get_payment.payment_status=enums.PaymentStatus.RETURNED.value

    db.commit()
    db.refresh(get_booking)
    db.refresh(get_payment)
    booking = trip_book_schema.BookingStatus(booking_id=get_booking.booking_id,
                                                booking_status=get_booking.booking_status)
    
    context = trip_book_schema.BookingStatusResponse(data=booking)

    return context

@route.get('/',response_model=trip_book_schema.BookingDetailResponse)
def get_booking_details(booking_id:int,
                        current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                        db:Session=Depends(database.get_db)):
    
    booking = db.query(models.TripBook).filter(models.TripBook.booking_id==booking_id).first()

    if not booking:
        return errors.NoCurrentBookings
    
    payment = db.query(models.Payment).filter(models.Payment.booking_id==booking_id).first()
    trip = db.query(models.Trip).filter(models.Trip.trip_id==booking.trip_id).first()

    if current_user_type == enums.UserType.DRIVER:
        if booking.driver_id != current_user.user_id:
            return errors.NotAuthorizedException
        user = db.query(models.User).filter(models.User.user_id==booking.passenger_id).first()
    elif current_user_type == enums.UserType.PASSENGER:
        if booking.passenger_id != current_user.user_id:
            return errors.NotAuthorizedException
        user = db.query(models.User).filter(models.User.user_id==trip.user_id).first()

    user = user_schema.GetUser.model_validate(user)

    trip = trip_schema.TripDetailBase.model_validate(trip)
    
    booking = trip_book_schema.TripBookBase.model_validate(booking)
    
    payment = payment_schema.PaymentDetail.model_validate(payment)


    booking_detail = trip_book_schema.BookingDetail(user=user,
                                                    booking_details=booking,
                                                    payment_details=payment,
                                                    trip=trip)
    

    context = trip_book_schema.BookingDetailResponse(data=booking_detail)

    return context

@route.get('/history',response_model=trip_book_schema.PassangerBookingListResponse)
def get_booking_history(current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                        db:Session=Depends(database.get_db)):
    
    if current_user_type != enums.UserType.PASSENGER:
        return errors.NotAuthorizedException
    
    bookings = (db.query(models.TripBook).join(models.Trip).filter(models.TripBook.passenger_id==current_user.user_id,
                                                                  or_(models.Trip.status==enums.TripStatus.COMPLETED,
                                                                      models.Trip.status==enums.TripStatus.CANCELLED,
                                                                      models.TripBook.booking_status==enums.BookingStatus.CANCELLED),
                                               or_(models.TripBook.booking_status==enums.BookingStatus.CANCELLED,
                                                   models.TripBook.booking_status==enums.BookingStatus.CONFIRMED))
                                                   .order_by(models.TripBook.booking_time)
                                                   .all())
    
    if len(bookings) < 1:
        return errors.NoCurrentBookings
    
    booking_list = []
    for booking in bookings:
        b = trip_book_schema.PassangerBookingList.model_validate(booking)
        b.driver_name = booking.driver.name
        b.trip = trip_schema.TripDetailBase.model_validate(booking.trip)
        booking_list.append(b)

    context = trip_book_schema.PassangerBookingListResponse(data=booking_list)
    return context

