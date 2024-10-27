from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host:str
    database_port:str
    database_username:str
    database_password:str
    database_name:str
    user_media_url:str
    document_media_url:str
    default_profile_photo_path:str
    secret_key:str
    token_expire_timeout:str
    algorithm:str
    aws_s3_access_key:str
    aws_s3_secret_access_key:str
    aws_s3_region:str
    aws_s3_bucket:str
    
    class Config:
        env_file='.env'


settings=Settings()