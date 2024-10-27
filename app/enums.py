from enum import Enum

class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class PaymentStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class TripStatus(Enum):
    UPCOMING = "UPCOMING"
    COMPLETED = "COMPLETED"
    ONGOING = "ONGOING"
    CANCELLED = "CANCELLED"

class UserType(Enum):
    DRIVER = "DRIVER"
    PASSENGER = "PASSENGER"