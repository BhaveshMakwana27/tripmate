from pydantic import BaseModel

class PaymentDetail(BaseModel):
    payment_id:int
    booking_id:int
    payment_method:str
    payment_status:str

    class Config:
        orm_mode=True