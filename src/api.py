from src.models import User, Like, Post, ActivityLog, log_activity, from_date
from src.app import api, db, app
import src.authentication as auth

import jwt
import datetime
from flask import request
from flask_restful import Resource
from sqlalchemy import func


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

        Request example (should be a single line):
            curl --header "Content-Type: application/json"
            -d '{"name":"Dima", "surname":"Antoniuk", "username": "sh", "password": "sh123"}'
            --request POST http://127.0.0.1:5000/api/users

        """

        args = request.get_json()

        if not args:
            # input data is invalid

            log_activity(f"user creation with a failure: no arguments passed")
            return {
                       "error": f"no arguments passed"
                   }, 404

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
            "username": new_user.username,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return {"token": token.decode("utf-8")}, 200


class Posts(Resource):
    def get(self):
        """
        :return: list of jsons of all posts

        example: curl http://127.0.0.1:5000/api/posts
        """

        posts = Post.query.all()

        posts_list = [post.json() for post in posts]

        log_activity("posts requested")

        return posts_list

    @auth.token_required
    def post(self, user):
        """
        API for creating a new post

        :param user: authenticated user, returned by auth.token_required function
        :return: json of a new created post

        example:
        curl -H "Content-Type: application/json" -H "X-Api-Key: <USER_TOKEN>"
        -d '{"text": "user has created a new post!!!"}' http://127.0.0.1:5000/api/posts

        where <USER_TOKEN> must be replaced by an authenticated user's token
        """

        args = request.get_json()

        if not args:
            log_activity("tried to add post without text", user_id=user.id)

            return {"error": "no post text provided"}

        new_post = Post(author_id=user.id, text=args["text"])

        db.session.add(new_post)
        db.session.commit()

        log_activity("new post added", user_id=user.id, post_id=new_post.id)

        return new_post.json()


class Likes(Resource):
    @auth.token_required
    def post(self, user):
        """
        API for a user to like/unlike some post. If post was already liked, this like will be deleted,
        post will be unliked (same as in Instagram). If user didn't like this post previously, like will be added

        :param user: authenticated user, who wants to like some post
        :return: data about new like or message that like was deleted

        example (should be a single line):
        curl -H "Content-Type: application/json" -H "X-Api-Key: <USER_TOKEN>"
        -d '{"uuid": "<POST_UUID>"}' http://127.0.0.1:5000/api/like

        Where <USER_TOKEN> must be replaced by user's jwt token, <POST_UUID> by uuid of a post,
        the user wants to like/unlike
        """

        args = request.get_json()

        if not args:
            log_activity("tried to like post without uuid", user_id=user.id)

            return {"error": "no post uuid provided"}

        post_uuid = args["uuid"]

        post = Post.query.filter(Post.uuid == post_uuid).first()

        if not post:
            log_activity(f"tried to like not existing post: {post_uuid}", user_id=user.id)

            return {"error": f"post with uuid {post_uuid} does not exist"}, 400

        like_query = Like.query.filter(Like.user_id == user.id, Like.post_id == post.id)

        if like_query.first():
            like_query.delete()
            db.session.commit()

            log_activity("unliked post", user_id=user.id, post_id=post.id)

            return {"message": "post was successfully unliked"}, 200
        else:
            like = Like(user_id=user.id, post_id=post.id)
            db.session.add(like)
            db.session.commit()

            log_activity("liked post", user_id=user.id, post_id=post.id)

            return like.json()


class UserStatistics(Resource):
    def get(self):
        """
        API for tracking user's activities: likes/unlikes, posts creation, logins and so on

        :return: json of all activities of a user

        example:
        curl -H "Content-Type: application/json" -d '{"username": "ooleksyshyn"}' -X GET http://127.0.0.1:5000/api/analytics/user


        """

        args = request.get_json()

        if not args:
            return {"error": "no username provided"}, 400

        username = args["username"]

        user = User.query.filter(User.username == username).first()

        if not user:
            return {"Invalid user statistic requested": f"{username}"}, 400

        actions = ActivityLog.query.filter(ActivityLog.user_id == user.id).all()

        return [action.json() for action in actions]


class LikeStatistics(Resource):
    def get(self):
        """
        API for statistics about likes on some post during some period of time, accumulated by date

        :return: json with data about likes on post during the given period of time (accumulated by date)

        example (should be a single line):
         curl -H "Content-Type: application/json"
         -d '{"uuid": "some uuid", "start_date":"2020-05-08", "end_date":"2020-05-09"}'
         -X GET http://127.0.0.1:5000/api/analytics/likes
        """

        args = request.get_json()

        if not args:
            return {"error": "no post uuid provided"}, 400

        post_uuid = args["uuid"]
        start_date = from_date(args.get("start_date", str(datetime.date.today())))
        end_date = from_date(args.get("end_date", str(datetime.date.today())))

        post = Post.query.filter(Post.uuid == post_uuid).first()

        if not post:
            return {"error": f"no such post {post_uuid}"}

        likes = db.session.query(Like.date, func.count(Like.date)).filter(
            Like.post_id == post.id,
            Like.date >= start_date,
            Like.date <= end_date
        ).group_by(Like.date).all()

        return {str(date): count for (date, count) in likes}, 200


api.add_resource(Users, "/api/users")
api.add_resource(Posts, "/api/posts")
api.add_resource(Likes, "/api/like")
api.add_resource(UserStatistics, "/api/analytics/user")
api.add_resource(LikeStatistics, "/api/analytics/likes")
