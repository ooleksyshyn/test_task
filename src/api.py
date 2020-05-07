from flask_restful import Resource, reqparse
from flask import jsonify
from src.models import User, Like, Post, ActivityLog
from src.app import api, db, app
import jwt
import datetime
from flask import request
import src.authentication as auth


def log_activity(action, **kwargs):
    """
    Function that adds actions to database table activity_log

    :param action: description of an activity
    :param kwargs: user_id, post_id if action is done by some user, and/or on some post
    """

    new_activity = ActivityLog(action=action, **kwargs)

    db.session.add(new_activity)
    db.session.commit()


class Users(Resource):
    def get(self):
        """
        :return: List of jsons with all users' data

        example: curl http://127.0.0.1:5000/api/users
        """

        users = User.query.all()

        users_list = [user.json() for user in users]

        log_activity("users list requested")

        return users_list, 200

    def post(self):

        """
        :return: a token of a new created user, or an error, if a user with given username already exists

        example:  curl --data "name=Olena&surname=Oleksyshyna&password=oleksyshyna123&username=ooolenka"
                  http://127.0.0.1:5000/api/users
        """

        args = request.get_json()

        new_user = User(**args)

        existing_user = User.query.filter(User.username == args['username']).all()

        if existing_user or (not args['name']) or (not args['surname']) or (not args['password']):
            # input data is invalid

            log_activity(f"user creation with a failure: {args['username']}")
            return {
                       "error": f"cant create user with name {args['name']}, "
                                f"surname {args['surname']}, username {args['username']}, password {args['password']}"
                   }, 404

        db.session.add(new_user)
        db.session.commit()

        log_activity(f"user created successfully: {args['username']}", user_id=new_user.id)

        token = jwt.encode({
            "user": new_user.username,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
            },
            app.config["SECRET_KEY"]
        )

        return {"token": token.decode("utf-8")}, 200


class Posts(Resource):
    def get(self):
        posts = Post.query.all()

        posts_list = [post.json() for post in posts]

        return posts_list

    @auth.token_required
    def post(self, user):
        pass



api.add_resource(Users, "/api/users")
