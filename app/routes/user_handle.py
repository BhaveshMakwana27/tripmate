from fastapi import APIRouter,Depends,UploadFile,File,Form
from fastapi.responses import RedirectResponse
from datetime import datetime
from app import database,models,utils,oauth2,file_handle,constants,errors,enums
from app.schemas import user_schema,token_schema,base_schema
from app.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import or_
import shutil
from typing import Union

route = APIRouter(prefix="/user")

@route.post("/",response_model=token_schema.Token)
def register(name: str = Form(...),
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
                    user_type:str = Form(enums.UserType.PASSENGER.value),
                    db:Session = Depends(database.get_db)
                    ):
    
    user_check = db.query(models.User).filter(or_(models.User.email==email,models.User.contact_no==contact_no))
    if user_check.first():
        if user_check.first().email==email:
            return errors.UserEmailExistException
        if user_check.first().contact_no==contact_no:
            return errors.UserContactExistException


    if user_type != enums.UserType.DRIVER.value and user_type != enums.UserType.PASSENGER.value:
        return errors.InvalidUserTypeException
      

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
    db.refresh(new_user)
    if profile_photo is not None:
        new_user_dir_path=f'{settings.user_media_url}{new_user.user_id}/'
        profile_photo.filename = f'{new_user.user_id}_profile.jpg'
        profile_file_path = f'{new_user_dir_path}{profile_photo.filename}'

        profile_file_path=file_handle.upload_file(file=profile_photo,filepath=f'{profile_file_path}')

        new_user.profile_photo=profile_file_path
        db.commit()
    db.refresh(new_user)


    access_token = oauth2.create_token({'user_id':new_user.user_id,'user_type':user_type})
    token = token_schema.Token(access_token=access_token,
                               token_type='Bearer'
                               )

    if user_type == enums.UserType.DRIVER:
        token.need_docs = True

    return token

@route.get("/",response_model=user_schema.GetProfileDetailsResponse)
def get_profile_details(db:Session = Depends(database.get_db),
                        current_user:models.User = Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type)):

    profile = user_schema.GetDriverUserDetails.model_validate(current_user)

    if current_user_type == enums.UserType.DRIVER:
        get_docs = db.query(models.UserIdProof).filter(models.UserIdProof.user_id==current_user.user_id).first()
        if get_docs is None:
            return errors.DocumentNotUploadedException
        doc_path = [get_docs.aadhar_card_front,get_docs.aadhar_card_back,get_docs.license_front,get_docs.license_back]
        doc_urls = file_handle.generate_presigned_url(doc_path)
        
        profile.documents = doc_urls

        return {'data' : profile}
    return {'data':profile}

@route.put("/",response_model=base_schema.BaseSchema)
def edit_profile(profile_photo:UploadFile=File(None),
                            name: str = Form(...),
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
    edit_user = user_schema.EditProfile(name=name,
                                        address_line=address_line,
                                        city=city,
                                        state=state,
                                        country=country,
                                        pincode=pincode,
                                        gender=gender.upper())
    

    if profile_photo is not None:
        new_user_dir_path=f'{settings.user_media_url}{user.first().user_id}/'
        profile_photo.filename = f'{user.first().user_id}_profile.jpg'
        profile_file_path = f'{new_user_dir_path}{profile_photo.filename}'

        profile_file_path=file_handle.upload_file(file=profile_photo,filepath=f'{profile_file_path}')

        user.first().profile_photo=profile_file_path

    user.first().updated_at = datetime.now()
    user.update(dict(edit_user))
    db.commit()
   
    context = base_schema.BaseSchema

    return context

@route.put('/update_profile_photo',response_model=base_schema.BaseSchema)
def edit_profile_photo( profile_photo:UploadFile=File(None),
                        db:Session=Depends(database.get_db),
                        current_user:models.User=Depends(oauth2.get_current_user)):
    
    if not profile_photo:
        return errors.FileSelectException
    new_user_dir_path=f'{settings.user_media_url}{current_user.user_id}/'
    profile_photo.filename = f'{current_user.user_id}_profile.jpg'
    profile_file_path = f'{new_user_dir_path}{profile_photo.filename}'

    profile_photo.filename = f'{current_user.user_id}_profile.jpg'
    new_url=file_handle.upload_file(file=profile_photo,
                            filepath=profile_file_path)
    current_user.profile_photo=new_url
    current_user.updated_at = datetime.now()
    db.commit()

    context = base_schema.BaseSchema
    return context

@route.post('/rating',response_model=base_schema.BaseSchema)
def give_rating(trip_id:int,current_user:models.User=Depends(oauth2.get_current_user),
                rating:int = Form(0),
                current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                db:Session=Depends(database.get_db)):
    
    
    if current_user_type!=enums.UserType.PASSENGER:
        return errors.NotAuthorizedException
    
    trip = db.query(models.Trip).filter(models.Trip.trip_id==trip_id,
                                        models.Trip.status==enums.TripStatus.COMPLETED).first()

    if trip is None:
        return errors.NoTripException

    driver = db.query(models.User).filter(models.User.user_id==trip.user_id).first()

    driver.rating_count += 1
    driver.ratings = (driver.ratings+rating)/driver.rating_count

    db.commit()
    
    context = base_schema.BaseSchema

    return context

@route.post("/upload_docs",response_model=base_schema.BaseSchema)
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
        return errors.NotAuthorizedException
    
    if not (len(aadhar_number)==16 and aadhar_number.isdigit()):
        return errors.InvalidAadharNumberException
    
    check_for_doc = db.query(models.UserIdProof).filter(or_(models.UserIdProof.user_id==current_user.user_id,models.UserIdProof.aadhar_number==aadhar_number))
    if check_for_doc.first():
        return errors.DocumentAlreadyUploadedException
    

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
    
    if len(file_urls) < 1:
        return errors.FileUploadException

    new_docs = user_schema.UploadUserDocs(user_id=current_user.user_id,
                                    aadhar_number=aadhar_number,
                                    aadhar_card_front=files_paths[0][1],
                                    aadhar_card_back=files_paths[1][1],
                                    license_front=files_paths[2][1],
                                    license_back=files_paths[3][1]
                                    )
    
    new_docs = models.UserIdProof(**dict(new_docs))

    db.add(new_docs)
    db.commit()

    context = base_schema.BaseSchema

    return context