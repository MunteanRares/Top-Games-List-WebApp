import requests
from flask import Flask, render_template, request, url_for, flash, abort
from functools import wraps
import os
from flask_login import UserMixin, login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from flask_ckeditor import CKEditor
from forms import AddGameForm, GameEditFull, RegisterForm, LoginForm, CommentForm

###########################
# CREATE APP SERVER
###########################
app = Flask(__name__)
app.secret_key = os.environ['SECRET_APP_KEY']
ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

###########################
# CONNECT SQLALCHEMY TO DATABASE
###########################
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///game-database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = F"postgresql://{os.environ.get('POSTGRE_USER')}:{os.environ.get('POSTGRE_PASS')}@localhost/{os.environ.get('POSTGRE_DB')}"
db = SQLAlchemy(app)

###########################
# CREATE FIRST TABLE named 'Games'
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

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    avatar = db.Column(db.String(250), nullable=False)

    #relationships
    user_games = relationship("UserGame", back_populates="user")

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



## Create to database.
with app.app_context():
    db.create_all()

###########################
# FUNCTIONS
###########################
def unregistered_only(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated:
            return abort(403)
        return func(*args, **kwargs)
    return wrapped

### REQUEST GAMES
def get_games_list_data(search_value):
    game_list = []
    params = {
        "key": os.environ.get("GAME_DB_KEY"),
        "search": search_value
    }

    response_game = requests.get("https://api.rawg.io/api/games", params=params)
    games_response = response_game.json()

    for game in games_response["results"]:
        game_list.append(game)
    return game_list

### SHORTEN DESCRIPTION
def cut_short_paragraph(text):
    cutoff = 250
    end_position = text.rfind('.', 0, cutoff)

    if end_position == -1:
        shortened_text = text[:250]
    else:
        shortened_text = text[:end_position + 1]

    return shortened_text

def cut_long_paragraph(text):
    cutoff = 1000
    end_position = text.rfind('.', 0, cutoff)

    if end_position == -1:
        shortened_text = text[:1000]
    else:
        shortened_text = text[:end_position + 1]

    return shortened_text

### YEAR FROM DATE
def get_year(date):
    temp = date.split("-")
    year = temp[0]
    return year

###########################
# INSERT FIRST VALUES TO 'Game'
###########################
# new_game = Game(
#     title="Euro Truck Simulator 2",
#     year=2012,
#     description="Travel across Europe as king of the road, a trucker who delivers important cargo across impressive"
#                 " distances! With dozens of cities to explore, your endurance, skill and speed will all be pushed to"
#                 " their limits. If you've got what it takes to be part of an elite trucking force, get behind the wheel"
#                 " and prove it!",
#     img_url="https://upload.wikimedia.org/wikipedia/en/0/0e/Euro_Truck_Simulator_2_cover.jpg"
# )
# Here we commit the changes
# with app.app_context():
#     db.session.add(new_game)
#     db.session.commit()


###########################
# WEBSITE ROUTES
###########################
@app.route('/')
def home():
    if current_user.is_authenticated:
        user_games = db.session.query(Game, UserGame).join(Game, UserGame.game_id == Game.id).filter(UserGame.user_id == current_user.id).all()

        return render_template("index.html", all_games=user_games)
    else:
        return render_template("index.html", all_games=[])


@app.route("/register", methods=["POST", "GET"])
@unregistered_only
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        if User.query.filter_by(email=email).first() is None:
            if request.form.get("password") == request.form.get("confirm_password"):
                name = request.form.get("name")
                hash_pas = generate_password_hash(password=request.form.get("password"),method="scrypt",salt_length=16)
                avatar_src = f"https://ui-avatars.com/api/?name={name}&background=random"

                new_user = User(
                    name=name,
                    email=email,
                    password=hash_pas,
                    avatar=avatar_src
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('home'))
            else:
                flash("The passwords you entered do not match. Please try again.")
        else:
            flash("Account already in use. Please log in instead.")
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
@unregistered_only
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(pwhash=user.password, password=request.form.get("password")):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid Credentials")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/edit', methods=["GET", "POST"])
@login_required
def update():
    id_of_game = request.args.get("game_id")
    game = UserGame.query.filter_by(game_id=id_of_game, user_id=current_user.id).first()
    # print(game)
    # print(current_user.id)
    # print(id_of_game)
    # print(game.id)

    if game.user_id == current_user.id:
        game_form = GameEditFull(
            rating=game.rating,
            review=game.note,
        )

        if game_form.validate_on_submit():
            game.rating = game_form.rating.data
            game.note = game_form.review.data
            db.session.commit()

            return redirect(url_for("view_card", game_id=id_of_game))
            # return redirect(location=url_for('home'))
    else:
        return abort(403)

    game_id = request.form.get("game_id") or id_of_game
    game_to_update = db.session.get(Game, game_id)
    return render_template("update.html", form=game_form, game_to_update=game_to_update, game=game)


@app.route("/delete")
@login_required
def delete():
    game_id = request.args.get("game_id")
    game_to_del = UserGame.query.filter_by(game_id=game_id, user_id=current_user.id).first()

    db.session.delete(game_to_del)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add-game", methods=["GET", "POST"])
@login_required
def add_game():
    form = AddGameForm()
    if form.validate_on_submit():
        game_name = request.form.get("game_name")
        game_results = get_games_list_data(game_name)
        print(game_results)
    else:
        game_results = []
    return render_template("add_game.html", form=form, game_results=game_results)


@app.route("/get_game")
@login_required
def get_game():
    game_id = request.args.get("game_id")
    params = {
        "key": os.environ.get("GAME_DB_KEY"),
    }
    response = requests.get(f"https://api.rawg.io/api/games/{game_id}", params=params)

    game_data = response.json()
    # print(game_data)

    game_name = game_data["name"]
    short_game_description = cut_short_paragraph(game_data["description_raw"])
    long_game_description = cut_long_paragraph(game_data["description_raw"])
    release_date = get_year(game_data["released"])
    img_background = game_data["background_image"]

    game = Game.query.filter_by(title=game_name).first()
    if not game:
        game = Game(
            title=game_name,
            year=release_date,
            short_description=short_game_description,
            long_description=long_game_description,
            img_url=img_background,
        )
        db.session.add(game)
        db.session.commit()

    existing_personal_game = UserGame.query.filter_by(game_id=game.id, user_id=current_user.id).first()
    if not existing_personal_game:
        personal_game = UserGame(
            rating = 1.0,
            note = "Add Your Review here!",
            user = current_user,
            game = game
        )
        db.session.add(personal_game)
        db.session.commit()
    return redirect(url_for('update', game_id=game.id))

@app.route("/view-card", methods=["GET", "POST"])
def view_card():
    game_id = request.args.get("game_id")
    print(game_id)
    game = Game.query.get(game_id)
    print(game)
    user_game = UserGame.query.filter_by(game_id = game_id, user_id = current_user.id).first()
    form = CommentForm()
    if form.validate_on_submit():
        
        return redirect(url_for("view_card", game_id=game_id))

    return render_template("view_card.html", game=game, user_game=user_game, form=form)

###########################
# RUN AND DEBUG SERVER
###########################
if __name__ == "__main__":
    app.run(debug=True)

