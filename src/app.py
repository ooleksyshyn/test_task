from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.config import DevConfig
from flask_restful import Api

app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)

api = Api(app)
