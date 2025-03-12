import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import logging

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="MeritPath Worker Service",
    # Disable automatic redirects for trailing slashes
    redirect_slashes=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGIN", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to MeritPath Worker Service"}

# Import routers - do this after creating the app to avoid circular imports
from app.api.routes.hello import router as hello_router
from app.api.routes.number_printer import router as number_printer_router

# Include routers from different modules
app.include_router(hello_router, prefix="/api/hello", tags=["hello"])
app.include_router(number_printer_router, prefix="/api/number-printer", tags=["number_printer"])

# Background tasks
from app.background_tasks import start_worker_service, stop_worker_service

@app.on_event("startup")
async def startup_event():
    # Start the worker service in the background
    asyncio.create_task(start_worker_service())

@app.on_event("shutdown")
async def shutdown_event():
    # Stop the worker service
    await stop_worker_service()