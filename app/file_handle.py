import shutil,boto3
from app.config import settings
from fastapi import UploadFile
from typing import List
from app import errors

def client():
    session = boto3.Session(aws_access_key_id=settings.aws_s3_access_key,
                            aws_secret_access_key=settings.aws_s3_secret_access_key,
                            region_name=settings.aws_s3_region)
    client = session.client('s3')
    return client


def upload_file(file:UploadFile,filepath,client=client()):
    try:
        client.upload_fileobj(file.file, 
                              settings.aws_s3_bucket, 
                              filepath, 
                              ExtraArgs={'ContentType': "image/jpeg"})
        
        file_url = f"https://{settings.aws_s3_bucket}.s3.amazonaws.com/{filepath}"
        return file_url
    except:
        return errors.FileUploadException
    

def upload_files(files_paths:List[List[UploadFile|str]],client=client()):
    try:
        file_urls = []
        for file in files_paths:
            client.upload_fileobj(file[0].file,
                                settings.aws_s3_bucket, 
                                file[1],
                                ExtraArgs={'ContentType': "image/jpeg"})
        
            file_urls.append(f"https://{settings.aws_s3_bucket}.s3.amazonaws.com/{file[1]}")
        return file_urls
    except:
        return errors.FileUploadException

def generate_presigned_url(files_paths:List[str],client=client(),expiration=3600):
    try:
        file_urls = []
        for file in files_paths:
            url = client.generate_presigned_url('get_object',
                                        Params={
                                                'Bucket': settings.aws_s3_bucket,
                                                'Key': file
                                                },
                                        ExpiresIn=expiration)
        
            file_urls.append(url)
        return file_urls
    except:
        return errors.DocumentNotUploadedException




