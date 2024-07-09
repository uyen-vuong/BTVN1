from fastapi import FastAPI
from routes.image_routes import router as image_router

app = FastAPI()

app.include_router(image_router, prefix="/image", tags=["Image Manipulation"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
