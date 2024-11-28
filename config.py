from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    HCAPTCHA_SECRET_KEY = os.getenv("HCAPTCHA_SECRET_KEY")
    HCAPTCHA_SITE_KEY = os.getenv("HCAPTCHA_SITE_KEY")
