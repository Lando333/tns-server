from dotenv import load_dotenv
import os

load_dotenv()   # loads secret key from .env

class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///app.db"

    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    CORS_ORIGINS = '*'

    STRIPE_PUBLIC_KEY = "pk_test_Tf1S5BkuE7m8m8LfpcfX82LN"
    STRIPE_SECRET_KEY = "sk_test_zhHsCoE4VH9JPgYo1E17b7o7"


# generate a secret key for Flask:
# python -c 'import os; print(os.urandom(16))'