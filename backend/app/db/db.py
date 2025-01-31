from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Create the database engine
engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)

# Create a sessionmaker
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for getting the session
async def get_db():
    """
    Dependency that provides a database session to the request.

    Yields:
        AsyncSession: The database session.
    """
    async with async_session() as session:
        yield session