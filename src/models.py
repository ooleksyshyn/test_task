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
    date = db.Column(db.Date, default=datetime.date.today())
    time = db.Column(db.Time, default=datetime.datetime.now().time())

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
            "date": str(self.date),
            "time": str(self.time)
        }


class Like(db.Model):
    """
    Describes a like given by some user to some post
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    date = db.Column(db.Date, default=datetime.date.today())
    time = db.Column(db.Time, default=datetime.datetime.now().time())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Like: id={self.id}, user_id={self.user_id}, post_id={self.post_id}, " \
               f"date={str(self.date)}, time={str(self.time)}>"

    def json(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id,
            "date": str(self.date),
            "time": str(self.time)
        }


class ActivityLog(db.Model):
    """
    Describes an activity by (optional) user (and/or) on some (optional) post,
    or just a message about what was done

    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=True)
    action = db.Column(db.String(255))
    date = db.Column(db.Date, default=datetime.date.today())
    time = db.Column(db.Time, default=datetime.datetime.now().time())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Activity: id={self.id}, user={self.user_id}, post={self.post_id}, " \
               f"action={self.action}, date={self.date}, time={self.time}>"

    def json(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id,
            "action": self.action,
            "date": str(self.date),
            "time": str(self.time)
        }


def clear_db():
    db.session.query(ActivityLog).delete()
    db.session.query(Like).delete()
    db.session.query(Post).delete()
    db.session.query(User).delete()

    db.session.commit()


def log_activity(action, **kwargs):
    """
    Function that adds actions to database table activity_log

    :param action: description of an activity
    :param kwargs: user_id, post_id if action is done by some user, and/or on some post
    """

    new_activity = ActivityLog(action=action, date=datetime.date.today(), time=datetime.datetime.now().time(), **kwargs)

    db.session.add(new_activity)
    db.session.commit()


def from_datetime(datetime_string):
    """
    Turns a string of datetime to date object
    """

    date = datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S").date()

    return date


def from_date(date_string):
    """
    Turns a string of date to date object
    """

    date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

    return date
