from datetime import datetime, timezone
from flask import Flask
import os
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship

###########################
# INIT THE WEB APP
###########################
app = Flask(__name__)
app.secret_key = os.environ['SECRET_APP_KEY']
app.jinja_env.add_extension('jinja2.ext.do')

###########################
# CONNECTING TO DATABASE
###########################
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///game-database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = F"postgresql://{os.environ.get('POSTGRE_USER')}:{os.environ.get('POSTGRE_PASS')}@localhost/{os.environ.get('POSTGRE_DB')}"
db = SQLAlchemy(app)


###########################
# DATABASE TABLES
###########################
class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    short_description = db.Column(db.String(250), nullable=False)
    long_description = db.Column(db.String(1500), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # ranking = db.Column(db.Integer)

    #relationships
    user_games = relationship("UserGame", back_populates="game")
    game_reviews = relationship("UserReview", back_populates="game")
    game_wishlist = relationship("Wishlist", back_populates="game")

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    avatar = db.Column(db.String(250), nullable=False)

    #relationships
    user_games = relationship("UserGame", back_populates="user")
    user_reviews = relationship("UserReview", back_populates="user")
    user_wishlist = relationship("Wishlist", back_populates="user")
    user_logs = relationship("Log", back_populates="user")

class Wishlist(db.Model):
    __tablename__ = "wishlist"
    id = db.Column(db.Integer, primary_key=True)
    ### RELATIONSHIPS
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="user_wishlist")

    game_id = db.Column(db.Integer, ForeignKey("games.id"))
    game = relationship("Game", back_populates="game_wishlist")

class UserGame(db.Model):
    __tablename__ = "user_games"
    id = db.Column(db.Integer, primary_key=True)

    # Edited game for user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="user_games")

    # MANY games for ONE user
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    game = relationship("Game", back_populates="user_games")

    rating = db.Column(db.Float)
    note = db.Column(db.String(250))


class UserReview(db.Model):
    __tablename__ = "user_reviews"
    id = db.Column(db.Integer, primary_key=True)

    ### RELATIONSHIPS
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="user_reviews")

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    game = relationship("Game", back_populates="game_reviews")

    rating = db.Column(db.Float)
    review = db.Column(db.String(450))
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    ### RELATIONSHIPS
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="user_logs")

    timestamp = db.Column(db.DateTime, nullable=False)
    table_name = db.Column(db.String(250))
    action = db.Column(db.String(250))
    record = db.Column(db.String(250))
    record_id = db.Column(db.Integer)

# with app.app_context():
#     db.session.execute(text("""
#     CREATE TABLE games (
#         id SERIAL PRIMARY KEY,
#         title VARCHAR(250) NOT NULL,
#         year INTEGER NOT NULL,
#         short_description VARCHAR(250) NOT NULL,
#         long_description VARCHAR(1500) NOT NULL,
#         img_url VARCHAR(250) NOT NULL);
#     """))
#
#     db.session.execute(text("""
#     CREATE TABLE users (
#         id SERIAL PRIMARY KEY,
#         name VARCHAR(250) NOT NULL,
#         email VARCHAR(250) NOT NULL UNIQUE,
#         password VARCHAR(250) NOT NULL,
#         avatar VARCHAR(250) NOT NULL);
#     """))
#
#     db.session.execute(text("""
#     CREATE TABLE wishlist (
#         id SERIAL PRIMARY KEY,
#         user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#         game_id INTEGER REFERENCES games(id) ON DELETE CASCADE);
#     """))
#
#     db.session.execute(text("""
#     CREATE TABLE user_games (
#         id SERIAL PRIMARY KEY,
#         user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#         game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
#         rating FLOAT,
#         note VARCHAR(250));
#     """))
#
#     db.session.execute(text("""
#     CREATE TABLE user_reviews (
#         id SERIAL PRIMARY KEY,
#         user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#         game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
#         rating FLOAT,
#         review VARCHAR(450),
#         date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);
#     """))
#
#     db.session.execute(text("""
#     CREATE TABLE logs (
#         id SERIAL PRIMARY KEY,
#         user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#         timestamp TIMESTAMPTZ NOT NULL,
#         table_name VARCHAR(250),
#         action VARCHAR(250),
#         record VARCHAR(250),
#         record_id INTEGER);
#     """))

