from fastapi import APIRouter,Depends,status,HTTPException,Form
from fastapi.responses import RedirectResponse,JSONResponse
from app import database,models,utils,oauth2,enums,errors
from app.schemas import token_schema
from app.config import settings
from sqlalchemy.orm import Session

route = APIRouter(prefix="/user")


@route.post("/login")
def login(contact_no: str = Form(...),
                    password: str = Form(...),
                    user_type : str = Form(enums.UserType.PASSENGER.value),
                    db:Session = Depends(database.get_db)
                    ):
    get_user = db.query(models.User).filter(models.User.contact_no==contact_no)
    if get_user.first() is None:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Credentials')
    
    if not utils.verify_password(password,get_user.first().password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Invalid Credentials')
    
    access_token = oauth2.create_token({'user_id':get_user.first().user_id,'user_type':user_type})
    response = token_schema.Token(access_token=access_token,token_type='Bearar')
    return response

@route.put("/switch_user",response_model=token_schema.Token) # to switch user between driver and passanger
def switch_user_type(current_user:models.User = Depends(oauth2.get_current_user),
                    current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):
    id = current_user.user_id
    if current_user_type == enums.UserType.DRIVER:
        new_access_token = oauth2.create_token({'user_id':id,"user_type":enums.UserType.PASSENGER.value})
    else :
        new_access_token = oauth2.create_token({'user_id':id,"user_type":enums.UserType.DRIVER.value})

    return {'access_token':new_access_token,'token_type':'Bearar'}

@route.get("/logout",response_model=token_schema.Token)
def logout(current_user:models.User=Depends(oauth2.get_current_user)):
    raise HTTPException(status_code=status.HTTP_302_FOUND)