import jwt
from functools import wraps
from flask import request
from src.models import User, Post, log_activity
from src.app import app, api
from flask_restful import Resource
import datetime


def token_required(func):
    @wraps(func)
    def authenticate(self, *args, **kwargs):
        """
        Decorator that is used to check if request contains a valid jwt token


        :param self: decorates methods, so it should positional argument self
        :param args, kwargs: other arguments, passed to decorated function
        :return: calls a decorated function with a 'user' passed as an argument, returns its result
        """

        token = request.headers.get("X-Api-Key", "")

        if not token:
            return {"token required": "invalid token"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        try:
            username = jwt.decode(token, app.config['SECRET_KEY'])['username']
        except (KeyError, jwt.ExpiredSignatureError):
            return {"token required": "token expired"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}
        except:
            return {"token required": "wrong token"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        user = User.query.filter(User.username == username).first()

        if not user:
            return {"token required": "invalid user"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        return func(self, user, *args, **kwargs)
    return authenticate


class Login(Resource):
    def get(self):
        """
        Allows user to login and receive its jwt token

        :return: json with token for this user
        """

        data = request.get_json()

        if not data:
            return {"error": 'No authorization data passed'}, 401

        user = User.query.filter(User.username == data.get("username")).first()

        if user is None or (user.password != data.get("password")):
            log_activity(f"user logined unsuccessfully: {data.get('username', '')}")
            return {"WWW-Authenticate": 'Basic realm="Authentication required"'}, 401

        token = jwt.encode({
            "username": user.username,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        log_activity("user logined successfully", user_id=user.id)

        return {"token": token.decode("utf-8")}, 200


api.add_resource(Login, "/api/login")
