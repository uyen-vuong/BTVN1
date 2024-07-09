from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import os
import json

router = APIRouter()

texts_file_path = 'data/texts.json'

if not os.path.exists(texts_file_path):
    with open(texts_file_path, 'w') as file:
        json.dump([], file)

@router.post("/insert_text")
async def insert_text_on_image(file: UploadFile = File(...), text: str = ""):
    if len(text) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text length exceeds 20 characters.")
    
    try:
        image = Image.open(io.BytesIO(await file.read()))
        draw = ImageDraw.Draw(image)
        
        font_size = int(min(image.size) / 4)
        font_path = "/Users/uyenvuong/Documents/dejavu-fonts-ttf-2.37/ttf/DejaVuMathTeXGyre.ttf"  
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        print(font)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
        draw.text(position, text, font=font, fill="red")

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_image = base64.b64encode(buffered.getvalue()).decode()

        image_path = f"static/processed_images/{file.filename}"
        image.save(image_path)

        with open(texts_file_path, 'r+') as file:
            texts = json.load(file)
            texts.append({"text": text, "image_path": image_path})
            file.seek(0)
            json.dump(texts, file)

        return {"base64_image": base64_image, "image_url": image_path}
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/texts", response_model=List[str])
async def get_texts():
    try:
        with open(texts_file_path, 'r') as file:
            texts = json.load(file)
        return [entry["text"] for entry in texts]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/check_text/{text}")
async def check_text(text: str):
    try:
        with open(texts_file_path, 'r') as file:
            texts = json.load(file)
        
        for entry in texts:
            if entry["text"] == text:
                return {"text": text, "image_path": entry["image_path"]}
        return {"detail": "Text not found."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
