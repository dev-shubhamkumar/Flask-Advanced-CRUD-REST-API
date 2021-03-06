import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPOGATE_EXCEPTIONS = True
UPLOADED_IMAGES_DEST = os.path.join("static", "images")  # manage root folder
SECRET_KEY = os.environ["APP_SECRET_KEY"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = [
    "access",
    "refresh",
]
