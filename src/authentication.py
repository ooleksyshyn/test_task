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
        token = request.headers.get("X-Api-Key", "")
        print(f"token: {token}, {request.headers}")

        if not token:
            return {"token required": "invalid token"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        try:
            username = jwt.decode(token, app.config['SECRET_KEY'])['username']
        except (KeyError, jwt.ExpiredSignatureError):
            return {"token required": "token expired"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        user = User.query.filter(User.username == username).first()

        if not user:
            return {"token required": "invalid user"}, 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        return func(self, user, *args, **kwargs)
    return authenticate


class Login(Resource):
    def get(self):
        auth = request.authorization
        user = User.query.filter(User.username == auth.get("username", "")).first()

        if user is None or (user.password != auth.get("password", "")):
            log_activity(f"user logined unsuccessfully: {auth.get('username', '')}")
            return {"WWW-Authenticate": 'Basic realm="Authentication required"'}, 401

        token = jwt.encode({
            "username": user.username,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        log_activity("user logined successfully", user_id=user.id)

        return {"token": token.decode("utf-8")}, 200


api.add_resource(Login, "/api/login")

# curl -H "Content-Type: application/json" -H "X-Api-Key:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Im9vbGVrc3lzaHluIiwiZXhwIjoxNTg4ODgxNzkxfQ.jvw8qwzblv5EJ8-zN96VyomBR7AV78NCewtYlNVXEu0" -d '{"uuid": "7b69a31a-0d4a-49d1-9e47-3c9ec8c894f0"}' http://127.0.0.1:5000/api/like
