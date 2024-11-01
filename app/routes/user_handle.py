from fastapi import APIRouter,Depends,UploadFile,File,Form
from datetime import datetime
from app import database,models,utils,oauth2,file_handle,constants,errors,enums
from app.schemas import user_schema,token_schema
from app.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import or_
import shutil
from typing import Optional

route = APIRouter(prefix="/user")

@route.post("/",response_model=user_schema.GetUser)
def register( name: str = Form(...),
                    email: str = Form(...),
                    contact_no: str = Form(...),
                    address_line:str = Form(...),
                    city:str = Form(...),
                    state:str = Form(...),
                    country:str = Form(...),
                    pincode:str = Form(...),
                    gender:str = Form(...),
                    password: str = Form(...),
                    profile_photo: UploadFile|None = File(None),
                    db:Session = Depends(database.get_db)
                    ):
    
    user_check = db.query(models.User).filter(or_(models.User.email==email,models.User.contact_no==contact_no))
    if user_check.first():
        if user_check.first().email==email:
            raise errors.UserEmailExistException
        if user_check.first().contact_no==contact_no:
            raise errors.UserContactExistException


    hashed_password = utils.hash_password(password) 
    user = user_schema.CreateUser(name=name,
                             email=email,
                             contact_no=contact_no,
                             address_line=address_line,
                             city=city,
                             state=state,
                             country=country,
                             pincode=pincode,
                             gender=gender.upper(),
                             password=hashed_password)
    

    
    new_user = models.User(**dict(user))
    db.add(new_user)
    db.commit()
    if profile_photo is not None:
        user = db.query(models.User).filter(models.User.email==email)

        new_user_dir_path=f'{settings.user_media_url}{user.first().user_id}/'
        profile_photo.filename = f'{user.first().user_id}_profile.jpg'
        profile_file_path = f'{new_user_dir_path}{profile_photo.filename}'

        profile_file_path=file_handle.upload_file(file=profile_photo,filepath=f'{profile_file_path}')

        user.first().profile_photo=profile_file_path
        db.commit()
    db.refresh(new_user)
    
    return new_user

@route.get("/",response_model=user_schema.GetUserDetails)
def get_profile_details(db:Session = Depends(database.get_db),current_user:models.User = Depends(oauth2.get_current_user)):
    return current_user

@route.get('/{user_id}',response_model=user_schema.GetUser)
def get_user_details(user_id:int,
                     db:Session = Depends(database.get_db),
                     current_user:models.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.user_id==user_id).first()
    return user

@route.put("/",response_model=user_schema.GetUserDetails)
def edit_profile(name: str = Form(...),
                            email: str = Form(...),
                            contact_no: str = Form(...),
                            address_line:str = Form(...),
                            city:str = Form(...),
                            state:str = Form(...),
                            country:str = Form(...),
                            pincode:str = Form(...),
                            gender:str = Form(...),
                            db:Session = Depends(database.get_db),
                            current_user:models.User = Depends(oauth2.get_current_user)
                        ):

    user = db.query(models.User).filter(models.User.user_id==current_user.user_id)
    edit_user = user_schema.UserBase(name=name,
                                        email=email,
                                        contact_no=contact_no,
                                        address_line=address_line,
                                        city=city,
                                        state=state,
                                        country=country,
                                        pincode=pincode,
                                        gender=gender)
    
    user.first().updated_at = datetime.now()
    user.update(dict(edit_user))
    db.commit()
   
    return user.first()

@route.put('/update_profile_photo')
def edit_profile_photo( profile_photo:UploadFile=File(...),
                        db:Session=Depends(database.get_db),
                        current_user:models.User=Depends(oauth2.get_current_user)):
    
    profile_photo.filename = f'{current_user.user_id}_profile.jpg'
    new_url=file_handle.upload_file(file=profile_photo,
                            filepath=current_user.profile_photo[40:])
    current_user.profile_photo=new_url
    current_user.updated_at = datetime.now()
    db.commit()
    return {'url':new_url}

@route.delete("")
def delete_profile(db:Session = Depends(database.get_db),current_user:models.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.user_id==current_user.user_id)
    shutil.rmtree(f'{settings.user_media_url}{user.first().user_id}')
    user.delete()
    db.commit()
    return True

@route.post("/upload_docs")
def upload_user_docs(aadhar_number:str = Form(),
                        aadhar_card_front:UploadFile = File(...),
                        aadhar_card_back :UploadFile = File(...), 
                        license_front :UploadFile = File(...),
                        license_back :UploadFile = File(...),
                        db:Session = Depends(database.get_db),
                        current_user:models.User = Depends(oauth2.get_current_user),
                        current_user_type:models.User = Depends(oauth2.get_current_user_type)
                    ):
    
    if current_user_type != enums.UserType.DRIVER:
        raise errors.NotAuthorizedException
    
    if not (len(aadhar_number)==16 and aadhar_number.isdigit()):
        raise errors.InvalidAadharNumberException
    
    check_for_doc = db.query(models.UserIdProof).filter(or_(models.UserIdProof.user_id==current_user.user_id,models.UserIdProof.aadhar_number==aadhar_number))
    if check_for_doc.first():
        raise errors.DocumentAlreadyUploadedException
    

    aadhar_card_front.filename = 'aadhar_front.jpg'
    aadhar_card_back.filename = 'aadhar_back.jpg'
    license_front.filename = 'license_front.jpg'
    license_back.filename = 'license_back.jpg'


    id_proof_path = f'{constants.USER_DOCS_DIR}{current_user.user_id}/'
    
    files_paths = [[aadhar_card_front,f'{id_proof_path}{aadhar_card_front.filename}'],
                   [aadhar_card_back, f'{id_proof_path}{aadhar_card_back.filename}'],
                   [license_front,f'{id_proof_path}{license_front.filename}'],
                   [license_back,f'{id_proof_path}{license_back.filename}']]
                 
    file_urls = file_handle.upload_files(files_paths)
    
    new_docs = user_schema.UploadUserDocs(user_id=current_user.user_id,
                                    aadhar_number=aadhar_number,
                                    aadhar_card_front=file_urls[0],
                                    aadhar_card_back=file_urls[1],
                                    license_front=file_urls[2],
                                    license_back=file_urls[3]
                                    )
    
    new_docs = models.UserIdProof(**dict(new_docs))

    db.add(new_docs)
    db.commit()

    return True

