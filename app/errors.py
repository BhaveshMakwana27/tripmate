# from fastapi import JSONResponse,status

# ''' User data Exceptions '''
# InvalidUserTypeException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="invalid user type")
# UserEmailExistException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="email address already used")
# UserContactExistException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="contact number already used")
# UserNotExistException = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,detail="user doesn't exist")
# CredentialsException = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could Not validate credentials',
#                                           headers={"WWW-Authenticate":"Bearer"})
# DocumentAlreadyUploadedException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='documents already uploaded')
# DocumentNotUploadedException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='upload documents first')
# DriverNotEligibleException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='You are not eligible for postring trip, please upload valid ID proofs')
# NotAuthorizedException = JSONResponse(status_code=status.HTTP_403_FORBIDDEN,detail='not authorized to perform this action')
# InvalidAadharNumberException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='invalid aadhar number')

# ''' File handling related Exception'''
# FileSelectException = JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='File Not Selected')
# FileUploadException = JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='File Not Uploaded')
# FileDeleteException = JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='File Not Deleted')

# ''' Vehicle data Related Exceptions '''
# NoVehicleException = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,detail='No Vehicle Available')
# VehicleExistsExeption = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Vehicle Already Exist')
# VehicleImageLimitExeption = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='only 4 images are acceptable to upload')
# InvalidVehicleException = JSONResponse(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Vehicle Detail')
# NoVehicleImageException = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Vehicle Image Id')

# ''' Trip data related Exceptions '''

# NoTripException = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,detail='No Trip Available')
# InvalidSeatCapacityException = JSONResponse(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid seat capacity provided')
# InvalidDateTimeException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Invalid Date and Time Provided')

# ''' Booking data related Exceptions '''

# InvalidBookingException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Invalid Booking')
# BookingFailedException = JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='Booking Failed')
# NoCurrentBookings = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,detail='No Bookings')
# AlreadyBookedException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='You have already booked this trip')
# BookingAlreadyCancelledException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='You have already cancelled booking for this trip')
# InvalidCancellationException = JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Cancellation can't be done.")

# ''' Payment related Exceptions '''

# InvalidPaymentMethod = JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Payment Method.')


# ''' Action Related Exception '''

# InvalidActionException =  JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Can not perform action now.')


from fastapi import status,HTTPException
from fastapi.responses import JSONResponse
from .schemas.base_schema import BaseSchema

''' User data Exceptions '''
InvalidUserTypeException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="invalid user type..", status=False))
        )

UserEmailExistException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="Email id already exist..", status=False))
        )

UserContactExistException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="Contact no already exist..", status=False))
        )

UserNotExistException = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=dict(BaseSchema(message="User Not exist..", status=False))
        )

CredentialsException = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=dict(BaseSchema(message="Could not validate credentials", status=False)),
        )

DocumentAlreadyUploadedException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="documents already uploaded", status=False)),
        )

DocumentNotUploadedException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="upload documents first", status=False)),
        )

DriverNotEligibleException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="You are not eligible for this action, please upload valid ID proofs", status=False)),
        )

NotAuthorizedException = JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=dict(BaseSchema(message="not authorized to perform this action", status=False)),
        )

InvalidAadharNumberException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="invalid aadhar number", status=False)),
        )

''' File handling related Exception'''
FileSelectException = JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=dict(BaseSchema(message="File Not Selected", status=False))
        )
FileUploadException = JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=dict(BaseSchema(message="File Not Uploaded", status=False))
        )
FileDeleteException = JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=dict(BaseSchema(message="File Not Deleted", status=False))
        )

''' Vehicle data Related Exceptions '''
NoVehicleException = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=dict(BaseSchema(message="No Vehicle Available", status=False))
        )

VehicleExistsExeption = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="Vehicle Already Exist", status=False))
        )

VehicleImageLimitExeption = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="only 5 images are acceptable to upload", status=False))
        )
InvalidVehicleException = JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=dict(BaseSchema(message="Invalid Vehicle Detail", status=False))
        )
NoVehicleImageException = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=dict(BaseSchema(message="Invalid Vehicle Image Id", status=False))
        )

''' Trip data related Exceptions '''

NoTripException = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=dict(BaseSchema(message="No Trip Available", status=False))
        )
        
InvalidSeatCapacityException = JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=dict(BaseSchema(message="Invalid seat capacity provided", status=False))
        )

InvalidDateTimeException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="Invalid Date and Time Provided", status=False))
        )

''' Booking data related Exceptions '''

InvalidBookingException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="Invalid Booking", status=False))
        )

BookingFailedException = JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=dict(BaseSchema(message="Booking Failed", status=False))
        )

NoCurrentBookings = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=dict(BaseSchema(message="No Bookings", status=False))
        )

AlreadyBookedException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="You have already booked this trip", status=False))
        )

BookingAlreadyCancelledException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="You have already cancelled booking for this trip", status=False))
        )

InvalidCancellationException = JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=dict(BaseSchema(message="Cancellation can't be done.", status=False))
        )

''' Payment related Exceptions '''

InvalidPaymentMethod = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content=dict(BaseSchema(message="Invalid Payment Method.", status=False))
        )


''' Action Related Exception '''

InvalidActionException =  JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, 
            content=dict(BaseSchema(message="Can not perform action now.", status=False))
        )