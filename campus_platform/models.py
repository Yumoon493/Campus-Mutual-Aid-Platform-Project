from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Integer, default=2)
    role = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    reward_points = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), default='other')
    status = db.Column(db.Integer, default=0)
    publisher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    taker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_time = db.Column(db.DateTime, server_default=func.now())


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    create_time = db.Column(db.DateTime, server_default=func.now())
