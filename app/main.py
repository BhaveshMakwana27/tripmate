from fastapi import FastAPI
from app.routes import user_handle,auth_handle,vehicle_handle,trip_handle,trip_book_handle
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]



app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins = origins,
                   allow_credentials = True,
                   allow_methods = ["*"],
                   allow_headers = ["*"]
                )

app.include_router(user_handle.route)
app.include_router(auth_handle.route)
app.include_router(vehicle_handle.route)
app.include_router(trip_handle.route)
app.include_router(trip_book_handle.route)