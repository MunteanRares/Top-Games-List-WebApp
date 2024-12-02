import requests
from debugpy.common.timestamp import current
from flask import render_template, request, url_for, flash, abort
from functools import wraps
import os
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from forms import AddGameForm, GameEditFull, RegisterForm, LoginForm, CommentForm
from tables import User, Game, UserGame, db, app, UserReview, Wishlist
import datetime
from sqlalchemy import desc, text, Table

###########################
# CREATE APP SERVER
###########################
login_manager = LoginManager()
login_manager.init_app(app)


###########################
# GET HOLD OF CURRENT USER
###########################
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


###########################
# CREATE DATABASE WITH TABLES
###########################
with app.app_context():
    db.create_all()

    # db.session.execute(text("""
    #     CREATE VIEW game_review_count AS
    #     SELECT
    #         games.title AS title,
    #         (SELECT COUNT (*)
    #         FROM user_reviews
    #         WHERE user_reviews.game_id = games.id) AS total_star_reviews,
    #         (SELECT COUNT (*)
    #         FROM user_reviews
    #         WHERE user_reviews.rating = 5
    #         AND user_reviews.game_id = games.id) AS five_star_reviews,
    #         (SELECT COUNT (*)
    #         FROM user_reviews
    #         WHERE user_reviews.rating = 4
    #         AND user_reviews.game_id = games.id) AS four_star_reviews,
    #         (SELECT COUNT (*)
    #         FROM user_reviews
    #         WHERE user_reviews.rating = 3
    #         AND user_reviews.game_id = games.id) AS three_star_reviews,
    #         (SELECT COUNT (*)
    #         FROM user_reviews
    #         WHERE user_reviews.rating = 2
    #         AND user_reviews.game_id = games.id) AS two_star_reviews,
    #         (SELECT COUNT (*)
    #         FROM user_reviews
    #         WHERE user_reviews.rating = 1
    #         AND user_reviews.game_id = games.id) AS one_star_reviews
    #     FROM games
    # """))
    # db.session.commit()

    game_review_count = Table('game_review_count', db.metadata, autoload_with=db.engine)


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

def get_year(date):
    temp = date.split("-")
    year = temp[0]
    return year



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

@app.route("/delete-wishlist")
@login_required
def delete_wishlist():
    game_id = request.args.get("game_id")
    game_to_del = Wishlist.query.get(game_id)

    db.session.delete(game_to_del)
    db.session.commit()
    return redirect(url_for('wishlist'))

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


@app.route("/add_game_to_wishlist")
@login_required
def add_game_to_wishlist():
    game_id = request.args.get("game_id")
    params = {
        "key": os.environ.get("GAME_DB_KEY"),
    }
    response = requests.get(f"https://api.rawg.io/api/games/{game_id}", params=params)
    game_data = response.json()

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
    existing_wishlist_game = Wishlist.query.filter_by(game_id=game.id, user_id=current_user.id).first()
    if not existing_wishlist_game:
        new_wishlist = Wishlist(
            game=game,
            user=current_user
        )
        db.session.add(new_wishlist)
        db.session.commit()
    return redirect(url_for("add_game"))

@app.route("/view-card", methods=["GET", "POST"])
@login_required
def view_card():
    game_id = request.args.get("game_id")
    print(game_id)
    game = Game.query.get(game_id)
    print(game)
    user_game = UserGame.query.filter_by(game_id = game_id, user_id = current_user.id).first()
    game_total_reviews = db.session.query(game_review_count).filter_by(title=game.title).first()

    form = CommentForm()
    if form.validate_on_submit():
        rating = request.form.get("rating")
        review_text = request.form.get("comment")

        new_user_review = UserReview(
            user = current_user,
            game = game,
            rating = rating,
            review = review_text,
            date= datetime.datetime.now(datetime.timezone.utc)
        )

        db.session.add(new_user_review)
        db.session.commit()
        return redirect(url_for("view_card", game_id=game_id))

    user_reviews = UserReview.query.order_by(desc(UserReview.date)).all()
    return render_template("view_card.html", game=game, user_game=user_game, form=form, user_reviews=user_reviews, game_total_reviews=game_total_reviews)

@app.route("/wishlist")
@login_required
def wishlist():
    all_wishlist = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template("wishlist.html", all_games=all_wishlist)





###########################
# RUN AND DEBUG SERVER
###########################
if __name__ == "__main__":
    app.run(debug=True)

