from pydantic import BaseModel,ConfigDict

class PaymentDetail(BaseModel):
    payment_id:int
    booking_id:int
    payment_method:str
    payment_status:str

    model_config = ConfigDict(from_attributes=True)