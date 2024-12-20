from fastapi import APIRouter,Depends,status,HTTPException,Form
from fastapi.responses import RedirectResponse,JSONResponse
from app import database,models,utils,oauth2,enums,errors
from app.schemas import token_schema,base_schema
from app.config import settings
from sqlalchemy.orm import Session

route = APIRouter(prefix="/user")


@route.post("/login",response_model=token_schema.Token)
def login(contact_no: str = Form(...),
                    password: str = Form(...),
                    user_type : enums.UserType = Form(enums.UserType.PASSENGER),
                    db:Session = Depends(database.get_db)
                    ):
    get_user = db.query(models.User).filter(models.User.contact_no==contact_no)
    if get_user.first() is None:    
        return errors.CredentialsException
    
    if not utils.verify_password(password,get_user.first().password):
        return errors.CredentialsException
    
    access_token = oauth2.create_token({'user_id':get_user.first().user_id,'user_type':user_type.value})
    response = token_schema.Token(access_token=access_token,token_type='Bearer')
    if user_type == enums.UserType.DRIVER:
        check_docs = db.query(models.UserIdProof).filter(models.UserIdProof.user_id == get_user.first().user_id)
        if check_docs.first() is None:
            response.need_docs = True
    return response

@route.put("/switch_user",response_model=token_schema.Token) # to switch user between driver and passanger
def switch_user_type(current_user:models.User = Depends(oauth2.get_current_user),
                    current_user_type:enums.UserType = Depends(oauth2.get_current_user_type),db:Session=Depends(database.get_db)):
    id = current_user.user_id
    response = token_schema.Token
    response.token_type='Bearer'
    if current_user_type == enums.UserType.DRIVER:
        new_access_token = oauth2.create_token({'user_id':id,"user_type":enums.UserType.PASSENGER.value})
        response.access_token = new_access_token
        response.need_docs = False

    elif current_user_type == enums.UserType.PASSENGER :
        new_access_token = oauth2.create_token({'user_id':id,"user_type":enums.UserType.DRIVER.value})
        response.access_token = new_access_token
        check_docs = db.query(models.UserIdProof).filter(models.UserIdProof.user_id == id)
        if check_docs.first() is None:
            response.need_docs = True


    return response

@route.post('/reset_password',response_model=base_schema.BaseSchema)
def reset_password(new_password:str=Form(...),
                   current_user:models.User=Depends(oauth2.get_current_user),
                   current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                   db:Session=Depends(database.get_db)):
    hashed_password = utils.hash_password(new_password)
    current_user.password=hashed_password
    db.commit()

    context = base_schema.BaseSchema
    return context

@route.get("/logout",response_model=base_schema.BaseSchema)
def logout(current_user:models.User=Depends(oauth2.get_current_user)):
    context = base_schema.BaseSchema
    return context