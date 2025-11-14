import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file that lives next to this config module
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")
