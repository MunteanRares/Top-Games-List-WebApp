from datetime import datetime, timezone
from flask import Flask
import os
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
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




