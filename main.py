from fastapi import FastAPI, File, UploadFile, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import boto3
import os
import json
import uuid
import io
from PIL import Image
from dotenv import load_dotenv

from database import engine, get_db, ProductImage, Base

# Load environment variables
load_dotenv()

app = FastAPI(title="FastRetail AI Classification")

# Ensure static and templates directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize AWS clients
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
)

rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
)
S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    products = db.query(ProductImage).order_by(ProductImage.created_at.desc()).all()
    
    # Process products to parse labels and generate secure URLs
    for product in products:
        # Parse labels
        try:
            product.parsed_labels = json.loads(product.labels)
        except:
            product.parsed_labels = []
        
        # Generate a secure presigned URL for viewing the image
        # We extract the key from the stored URL (the part after the last slash)
        try:
            s3_key = product.s3_url.split("/")[-1]
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=3600 # 1 hour
            )
            product.display_url = presigned_url
        except:
            product.display_url = product.s3_url

    return templates.TemplateResponse(request=request, name="index.html", context={"products": products})

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not S3_BUCKET_NAME:
        raise HTTPException(status_code=500, detail="AWS_S3_BUCKET_NAME is not set in environment variables.")

    # 1. Process and convert image to JPG to ensure Rekognition compatibility
    try:
        # Read the file into a PIL Image
        file_content = await file.read()
        img = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB (in case of PNG with alpha or WebP)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Save back to a BytesIO object as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
        final_contents = buffer.getvalue()
        
        # Generate a unique filename with .jpg extension
        unique_filename = f"{uuid.uuid4()}.jpg"
        content_type = "image/jpeg"
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la imagen: {str(e)}")

    # 2. Upload to S3
    try:
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=unique_filename, Body=final_contents, ContentType=content_type)
        # Store the permanent base URL in DB
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")

    # 3. Analyze with Amazon Rekognition
    try:
        response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': S3_BUCKET_NAME, 'Name': unique_filename}},
            MaxLabels=10,
            MinConfidence=75.0
        )
        labels = [{"Name": label["Name"], "Confidence": round(label["Confidence"], 2)} for label in response['Labels']]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process with Rekognition: {str(e)}")

    # 4. Save to database
    db_product = ProductImage(
        filename=file.filename,
        s3_url=s3_url,
        labels=json.dumps(labels)
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # 5. Generate secure URL for the immediate response
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': unique_filename},
        ExpiresIn=3600
    )

    return {
        "message": "Image classified successfully", 
        "id": db_product.id, 
        "labels": labels, 
        "s3_url": presigned_url # Send the secure URL to frontend
    }

@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductImage).order_by(ProductImage.created_at.desc()).all()
    result = []
    for product in products:
        try:
            labels = json.loads(product.labels)
        except:
            labels = []
        result.append({
            "id": product.id,
            "filename": product.filename,
            "s3_url": product.s3_url,
            "labels": labels,
            "created_at": product.created_at
        })
    return result
