from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import route_games
from app.db.db import engine
from app.db.models import Base

# Initialize the FastAPI app
app = FastAPI()

# List of allowed origins for CORS
origins = [
    "http://localhost:3000",  # React development server
    "http://localhost:8000",
    # Add other origins as needed
]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup():
    """
    Event handler for the startup event.

    This function creates all the database tables defined in the models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Define a root endpoint
@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to my FastAPI project!"}

# Include the games router with a prefix and tags
app.include_router(route_games.router, prefix="/games", tags=["Games"])