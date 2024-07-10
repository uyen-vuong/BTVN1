from fastapi import FastAPI
from routes.image_routes import router as image_router

app = FastAPI()

app.include_router(image_router, prefix="/image", tags=["Image Manipulation"])



