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
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETURNED = "RETURNED"

class PaymentMethod(Enum):
    ONLINE = "ONLINE"
    CASH = "CASH"

class TripStatus(Enum):
    UPCOMING = "UPCOMING"
    COMPLETED = "COMPLETED"
    ONGOING = "ONGOING"
    CANCELLED = "CANCELLED"

class UserType(Enum):
    DRIVER = "DRIVER"
    PASSENGER = "PASSENGER"