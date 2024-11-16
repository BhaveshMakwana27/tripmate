from fastapi import APIRouter,HTTPException,status,UploadFile,File,Form,Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import database,models,oauth2,constants,file_handle,errors,enums
from app.schemas import vehicle_schema
from app.config import settings
from typing import List

route = APIRouter(prefix='/vehicle')

@route.post('/upload_vehicle')
def upload_vehicle(model:str = Form(...),
                    type:str = Form(...),
                    seat_capacity:str = Form(...),
                    registration_number:str = Form(...),
                    rc_book_front:UploadFile = File(...),
                    rc_book_back:UploadFile = File(...),
                    vehicle_images:List[UploadFile] = File(...),
                    db:Session = Depends(database.get_db),
                    current_user:models.User = Depends(oauth2.get_current_user),
                    current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)
                    ):

    if current_user_type is not enums.UserType.DRIVER:
        raise errors.NotAuthorizedException

    if not db.query(models.UserIdProof).filter(models.UserIdProof.user_id==current_user.user_id).first():
        raise errors.DocumentNotUploadedException

    if db.query(models.Vehicle).filter(models.Vehicle.registration_number==registration_number).first() is not None:
        raise errors.VehicleExistsExeption
    
    if len(vehicle_images)>4:
        raise errors.VehicleImageLimitExeption
    
    document_path = f'{constants.VEHICLE_DOCS_DIR}{current_user.user_id}_{registration_number}/'
    vehicle_photo_path = f'{settings.user_media_url}{current_user.user_id}{constants.VEHICLE_PHOTOS_DIR}{registration_number}/'

    rc_book_front.filename = 'rc_front.jpg'
    rc_book_back.filename = 'rc_back.jpg'

    rc_paths = [[rc_book_front,f'{document_path}{rc_book_front.filename}'],
                [rc_book_back,f'{document_path}{rc_book_back.filename}']
                ]

    file_handle.upload_files(rc_paths)

    vehicle = vehicle_schema.UploadVehicle(model=model,
                                           type=type,
                                           seat_capacity=seat_capacity,
                                           registration_number=registration_number,
                                           rc_book_front=f'{document_path}{rc_book_front.filename}',
                                           rc_book_back=f'{document_path}{rc_book_back.filename}'
                                           )


    new_vehicle = models.Vehicle(user_id=current_user.user_id,**dict(vehicle))
    db.add(new_vehicle)
    db.commit()
    
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.registration_number==registration_number)
    if vehicle.first() is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,detail='Vehicle is not added properly')
    
    vehicle_id = vehicle.first().vehicle_id
    for index,image in enumerate(vehicle_images):
        image.filename = f'{index+1}_vimg.jpg'
        file_url = file_handle.upload_file(image,f'{vehicle_photo_path}{image.filename}')
        vehicle_image = models.VehicleImage(vehicle_id=vehicle_id,image_path=file_url)
        db.add(vehicle_image)
    
    db.commit()

    return vehicle.first()

@route.get('',response_model=List[vehicle_schema.VehicleList])
def get_vehicles(db:Session=Depends(database.get_db),
                 current_user:models.User=Depends(oauth2.get_current_user),
                 current_user_type:enums.UserType = Depends(oauth2.get_current_user_type)):


    if current_user_type != enums.UserType.DRIVER:
        raise errors.NotAuthorizedException

    vehicles = (db.query(models.Vehicle, models.VehicleImage.image_path.label('image_path'))
                .filter(models.Vehicle.user_id==current_user.user_id)
                .join(models.VehicleImage, models.Vehicle.vehicle_id == models.VehicleImage.vehicle_id, isouter=True)
                .distinct(models.Vehicle.vehicle_id).all())
    
    if not vehicles:
        raise errors.NoVehicleException
    
    return vehicles

@route.put('/')
def edit_vehicle_details(vehicle_id:int,
                        type:str|None=Form(None),
                         model:str|None=Form(None),
                         seat_capacity:int|None=Form(None),
                         current_user:models.User=Depends(oauth2.get_current_user),
                         current_user_type:enums.UserType=Depends(oauth2.get_current_user_type),
                         db:Session=Depends(database.get_db)):

    if current_user_type!=enums.UserType.DRIVER:
        raise errors.NotAuthorizedException

    vehicle = db.query(models.Vehicle).filter(models.Vehicle.vehicle_id==vehicle_id,models.Vehicle.user_id==current_user.user_id).first()

    if not vehicle:
        raise errors.NoVehicleException
    
    if model:
        vehicle.model=model
    if type:
        vehicle.type=type
    if seat_capacity:
        vehicle.seat_capacity=seat_capacity

    db.commit()

    return True

@route.get('/', response_model=vehicle_schema.VehicleDetails)
def get_vehicle_details(vehicle_id:int,
                        db:Session=Depends(database.get_db),
                        current_user:models.User=Depends(oauth2.get_current_user),
                        current_user_type:enums.UserType=Depends(oauth2.get_current_user_type)):
    
    if current_user_type != enums.UserType.DRIVER:
        raise errors.NotAuthorizedException

    vehicle_images = (db.query(models.VehicleImage.vehicle_id,
                                 func.array_agg((models.VehicleImage.image_path)
                                ).label('images')
                        ).filter(models.VehicleImage.vehicle_id==vehicle_id)
                        .group_by(models.VehicleImage.vehicle_id)
                        .subquery())

    vehicle = (db.query(models.Vehicle,vehicle_images.c.images)
                .join(vehicle_images,models.Vehicle.vehicle_id==vehicle_images.c.vehicle_id)
                .filter(models.Vehicle.vehicle_id==vehicle_id,models.Vehicle.user_id==current_user.user_id)
                .first())
    


    if vehicle:
        vehicle_obj, images = vehicle
        rc_paths = [vehicle_obj.rc_book_front,vehicle_obj.rc_book_back]

        rc_paths = file_handle.generate_presigned_url(rc_paths)

        vehicle_data = {
            "vehicle_id": vehicle_obj.vehicle_id,
            "type": vehicle_obj.type,
            "model": vehicle_obj.model,
            "seat_capacity": vehicle_obj.seat_capacity,
            "registration_number": vehicle_obj.registration_number,
            "rc_book_front":rc_paths[0],
            "rc_book_back":rc_paths[1],
            "images": images  
        }
    else:
        raise errors.NoVehicleException
    return vehicle_data

@route.get('/vehicle_images/{vehicle_id}',response_model=vehicle_schema.VehicleImages)
def get_vehicle_images(vehicle_id:int,
                       db:Session = Depends(database.get_db),
                       current_user:models.User = Depends(oauth2.get_current_user)):

    images = (db.query(models.VehicleImage.image_path.label('image'))
                       .filter(models.VehicleImage.vehicle_id==vehicle_id).all())


    if len(images)==0:
        raise errors.NoVehicleException
    
    return {"images":[image.image for image in images]}

@route.delete('/{vehicle_id}')
def delete_vehicle(vehicle_id:int,
                   db:Session = Depends(database.get_db),
                   current_user:models.User = Depends(oauth2.get_current_user),
                   current_user_type:models.User = Depends(oauth2.get_current_user_type)
                ):

    if current_user_type is not enums.UserType.DRIVER:
        raise errors.NotAuthorizedException
    
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.vehicle_id==vehicle_id)

    if not vehicle.first():
        raise errors.NoVehicleException
    
    if vehicle.first().user_id != current_user.user_id:
        raise errors.NotAuthorizedException
    
    
    vehicle_path = f'{settings.user_media_url}{current_user.user_id}{constants.VEHICLE_PHOTOS_DIR}{vehicle.first().registration_number}'

    file_handle.delete_file(vehicle_path)

    vehicle.delete()
    db.commit()

    return True