class BaseConfig:
    pass


class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_NAME = "testdb"
    DB_USERNAME = "oleksii"
    DB_PASSWORD = "1"
    DB_HOST = "localhost"
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SECRET_KEY = "1"
