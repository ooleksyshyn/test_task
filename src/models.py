from src.app import db
import uuid
import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return f"<User: id={self.id}, name={self.name}, surname={self.surname}, " \
               f"username={self.username}, password={self.password}>"

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "username": self.username,
            "password": self.password
        }


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.Text, nullable=False)
    uuid = db.Column(db.String(255), unique=True)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return f"<Post: id={self.id}, author_id={self.author_id}>, text={self.text}, uuid={self.uuid}"

    def json(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "text": self.text,
            "uuid": self.uuid,
            "datetime": str(self.datetime)
        }


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Like: id={self.id}, user_id={self.user_id}, post_id={self.post_id}, date={self.date}>"

    def json(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id,
            "date": str(self.datetime)
        }


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=True)
    action = db.Column(db.String(255))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Activity: id={self.id}, user={self.user_id}, post={self.post_id}, " \
               f"action={self.action}, time={self.datetime}>"

    def json(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id,
            "action": self.action,
            "time": str(self.datetime)
        }
