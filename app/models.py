from sqlalchemy import Column,String,Integer,TIMESTAMP,text,ForeignKey,Double,Enum,Interval,Computed
from sqlalchemy.orm import relationship
from app.database import Base
from app import enums
from app.config import settings

class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    contact_no = Column(String,nullable=False,unique=True)
    address_line = Column(String,nullable=False)
    city = Column(String,nullable=False)
    state = Column(String,nullable=False)
    country = Column(String,nullable=False)
    pincode = Column(Integer,nullable=False)
    gender = Column(Enum(enums.Gender),nullable=False)
    password = Column(String,nullable=False)
    profile_photo = Column(String,nullable=False,server_default=settings.default_profile_photo_path)
    ratings = Column(Double,nullable=False,server_default='0.0')
    rating_count = Column(Integer,nullable=False,server_default='0')
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

class Vehicle(Base):
    __tablename__ = 'vehicle'

    vehicle_id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('user.user_id',ondelete="CASCADE"),nullable=False)
    type = Column(String,nullable=False)
    model = Column(String,nullable=False)
    seat_capacity = Column(Integer,nullable=False)
    registration_number = Column(String,nullable=False,unique=True)
    rc_book_front = Column(String,nullable=False)
    rc_book_back = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

    owner = relationship("User")

class VehicleImage(Base):
    __tablename__ = 'vehicle_image'
    image_id = Column(Integer,primary_key=True)
    vehicle_id = Column(Integer,ForeignKey('vehicle.vehicle_id',ondelete='CASCADE'),nullable=False)
    image_path = Column(String,nullable=False)

    vehicle = relationship('Vehicle')

class UserIdProof(Base):
    __tablename__ = 'user_id_proof'

    user_id = Column(Integer,ForeignKey('user.user_id',ondelete='CASCADE'),primary_key=True)
    aadhar_number = Column(String(16),unique=True,nullable=False)
    aadhar_card_front = Column(String,nullable=False)
    aadhar_card_back = Column(String,nullable=False)
    license_front = Column(String,nullable=False)
    license_back = Column(String,nullable=False)
    
    owner = relationship('User')

class Trip(Base):
    __tablename__ = "trip"

    trip_id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('user.user_id',ondelete='CASCADE'),nullable=False)
    vehicle_id = Column(Integer,ForeignKey('vehicle.vehicle_id',ondelete='CASCADE'),nullable=False)
    source_address_line = Column(String,nullable=False)
    source_city = Column(String,nullable=False)
    source_state = Column(String,nullable=False)
    source_country = Column(String,nullable=False)
    source_pincode = Column(String,nullable=False)
    destination_address_line = Column(String,nullable=False)
    destination_city = Column(String,nullable=False)
    destination_state = Column(String,nullable=False)
    destination_country = Column(String,nullable=False)
    destination_pincode = Column(String,nullable=False)
    seats_available = Column(Integer,nullable=False)
    fees_per_person = Column(Integer,nullable=False)
    status = Column(Enum(enums.TripStatus), nullable=False, server_default=enums.TripStatus.UPCOMING.value)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    duration = Column(Interval,Computed('end_time - start_time'))
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

    driver = relationship('User')
    vehicle = relationship('Vehicle')

class TripBook(Base):
    __tablename__ = "trip_book"

    booking_id = Column(Integer,primary_key=True)
    trip_id = Column(Integer,ForeignKey("trip.trip_id"),nullable=False)
    driver_id = Column(Integer,ForeignKey("user.user_id"),nullable=False)
    passenger_id = Column(Integer,ForeignKey("user.user_id"),nullable=False)
    booking_status = Column(Enum(enums.BookingStatus),nullable=False,server_default=enums.BookingStatus.CONFIRMED.value)
    payable_amount = Column(Integer,nullable=False)
    seat_count = Column(Integer,nullable=False)
    booking_time = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))

    trip = relationship('Trip')
    passenger = relationship('User',foreign_keys=[passenger_id])
    driver = relationship('User',foreign_keys=[driver_id])

class Payment(Base):
    __tablename__ = 'payment'

    payment_id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("trip_book.booking_id"), nullable=False)
    amount = Column(Integer, nullable=False)
    payment_method = Column(Enum(enums.PaymentMethod), nullable=False,server_default=enums.PaymentMethod.CASH.value)
    payment_time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    payment_status = Column(Enum(enums.PaymentStatus), nullable=False, server_default=enums.PaymentStatus.PENDING.value)
    booking = relationship('TripBook')

# class TripCompletionCheck(Base):
#     __tablename__ = 'trip_completion_check'

#     booking_id = Column(Integer,ForeignKey("trip_book.booking_id",ondelete='CASCADE'),nullable=False)
#     passenger_confirmation = Column(Boolean, nullable=False, server_default='false')
#     driver_confirmation = Column(Boolean, nullable=False, server_default='false')
#     trip_completed = Column(Boolean, nullable=False, server_default='false')

#     trip_book = relationship("TripBook")