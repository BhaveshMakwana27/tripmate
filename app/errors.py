from fastapi import HTTPException,status

''' User data Exceptions '''
InvalidUserTypeException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="invalid user type")
UserEmailExistException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="email address already used")
UserContactExistException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="contact number already used")
UserNotExistException = HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user doesn't exist")
CredentialsException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could Not validate credentials',
                                          headers={"WWW-Authenticate":"Bearer"})
DocumentAlreadyUploadedException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='documents already uploaded')
DocumentNotUploadedException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='upload documents first')
DriverNotEligibleException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='You are not eligible for postring trip, please upload valid ID proofs')
NotAuthorizedException = HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='not authorized to perform this action')
InvalidAadharNumberException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='invalid aadhar number')

''' File handling related Exception'''
FileSelectException = HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='File Not Selected')
FileUploadException = HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='File Not Uploaded')
FileDeleteException = HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='File Not Deleted')

''' Vehicle data Related Exceptions '''
NoVehicleException = HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No Vehicle Available')
VehicleExistsExeption = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Vehicle Already Exist')
VehicleImageLimitExeption = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='only 4 images are acceptable to upload')
InvalidVehicleException = HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Vehicle Detail')
NoVehicleImageException = HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Vehicle Image Id')

''' Trip data related Exceptions '''

NoTripException = HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No Trip Available')
InvalidSeatCapacityException = HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid seat capacity provided')
InvalidDateTimeException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Invalid Date and Time Provided')

''' Booking data related Exceptions '''

InvalidBookingException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='Invalid Booking')
BookingFailedException = HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='Booking Failed')
NoCurrentBookings = HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No Bookings')
AlreadyBookedException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='You have already booked this trip')
BookingAlreadyCancelledException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail='You have already cancelled booking for this trip')
InvalidCancellationException = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Cancellation can't be done.")

''' Payment related Exceptions '''

InvalidPaymentMethod = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Payment Method.')