# test_config.py (sirf test ke liye)
from app.config import settings

print("DATABASE_URL:", settings.DATABASE_URL)
print("GROQ_API_KEY :", "**** (hidden)" if settings.GROQ_API_KEY else "Missing")
print("SECRET_KEY  :", settings.SECRET_KEY[:10] + "..." if settings.SECRET_KEY else "Not set")

