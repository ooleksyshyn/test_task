import jwt
from functools import wraps
from flask import request
from src.models import User, Post
from src.app import app, api
from flask_restful import Resource
import datetime


def token_required(func):
    @wraps(func)
    def authenticate(self, *args, **kwargs):
        token = request.headers.get("X-Api-Key", "")

        if not token:
            return "", 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        try:
            username = jwt.decode(token, app.config['SECRET_KEY'])['username']
        except (KeyError, jwt.ExpiredSignatureError):
            return "", 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        user = User.query.filter(User.username == username)

        if not user:
            return "", 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        if kwargs:
            post = Post.query.filter(Post.uuid == kwargs["uuid"]).first()

            if not post:
                return "", 404
            if post.author_id != user.id:
                return "", 401, {"WWW-Authenticate": 'Basic realm="Authentication required"'}

        return func(self, user, *args, **kwargs)
    return authenticate


class Login(Resource):
    def get(self):
        auth = request.authorization
        user = User.query.filter(User.username == auth.get("username", "")).first()

        if user is None or (user.password != auth.get("password", "")):
            return {"WWW-Authenticate": 'Basic realm="Authentication required"'}, 401

        token = jwt.encode({
            "username": user.username,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return {"token": token.decode("utf-8")}, 200


api.add_resource(Login, "/api/login")
