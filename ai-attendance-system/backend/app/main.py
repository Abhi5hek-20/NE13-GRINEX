from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from .models import create_tables
from .routes import auth_router, lecturer_router, student_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Attendance System",
    description="An intelligent attendance management system using facial recognition",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Mount static files for uploaded images
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(lecturer_router, prefix="/lecturer", tags=["Lecturer"])
app.include_router(student_router, prefix="/student", tags=["Student"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Attendance System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)