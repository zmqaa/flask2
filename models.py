from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False) #唯一，不可为空
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(123), unique=True, nullable=False)
    avatar = db.Column(db.String(200))  #头像的url

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_passsword(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<用户 {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  #默认时间
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<文章 {self.title}'



