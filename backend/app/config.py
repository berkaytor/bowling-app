from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings for the application.

    Attributes:
        DATABASE_URL (str): The database connection URL.
    """
    DATABASE_URL: str
    OPENAI_API_KEY: str

    class Config:
        """
        Configuration for the Settings class.

        Attributes:
            env_file (str): The path to the environment file.
        """
        env_file = ".env"

# Instantiate the settings
settings = Settings()