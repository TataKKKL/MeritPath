import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Core API Backend",
    # Disable automatic redirects for trailing slashes
    redirect_slashes=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI backend"}

# Import routers - do this after creating the app to avoid circular imports
from app.api.routes.hello import router as hello_router
from app.api.routes.sqs import router as sqs_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.paper_routes import router as paper_router

# Include routers from different modules
app.include_router(hello_router, prefix="/api/hello", tags=["hello"])
app.include_router(sqs_router, prefix="/api/sqs", tags=["sqs"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(paper_router, prefix="/api/papers", tags=["papers"])