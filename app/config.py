import os
from dotenv import load_dotenv

# Load environment variables from the .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Set the BASE_DIR for the project directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Default upload folder location (can be overridden in the .env file)
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'app', 'static', 'uploads'))

    # Mask folder path inside the UPLOAD_FOLDER for specific task-based image storage
    MASK_FOLDER = os.path.join(UPLOAD_FOLDER, 'masks')

    # Optional: Define a maximum content length for file uploads (e.g., 16MB limit)
    #MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    MAX_CONTENT_LENGTH = None 
