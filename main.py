from cProfile import label

import requests
from flask import Flask, render_template, request, url_for
from flask_ckeditor import CKEditorField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField, FloatField, validators
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor
from wtforms.fields.numeric import IntegerField

###########################
# CREATE APP SERVER
###########################
app = Flask(__name__)
app.secret_key = "aijsdoiasjoiada"
ckeditor = CKEditor(app)

###########################
# CONNECT SQLALCHEMY TO DATABASE
###########################
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///game-database.db"
db = SQLAlchemy(app)


###########################
# CREATE CLASSES FOR FORMS
###########################
class UpdateForm(FlaskForm):
    rating = FloatField(label="Your Rating", validators=[validators.DataRequired()])
    review = StringField(label="Your Review", validators=[validators.length(max=75)])
    submit = SubmitField(label="Submit")


class AddGameForm(FlaskForm):
    game_name = StringField(label="Game Name", validators=[validators.DataRequired()])
    submit = SubmitField(label="Search")

class GameEditFull(FlaskForm):
    title = StringField(label="Game Title", validators=[validators.DataRequired()])
    year = IntegerField(label="Game Year", validators=[validators.DataRequired()])
    rating = FloatField(label="Game Rating", validators=[validators.DataRequired()])
    review = StringField(label="Game Review", validators=[validators.DataRequired()])
    description = CKEditorField(label="Game Description")
    submit = SubmitField(label="Update")

###########################
# CREATE FIRST TABLE named 'Games'
###########################
class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    year: Mapped[int]
    rating: Mapped[float]
    review: Mapped[str]
    description: Mapped[str]
    img_url: Mapped[str]
    ranking: Mapped[int] = mapped_column(nullable=True)
### Create to database.
with app.app_context():
    db.create_all()


###########################
# FUNCTIONS
###########################
### VALIDATE ON UPDATE PAGE
# def validate_update():
#     game_id_from_form = request.form.get("id")
#     new_review = request.form.get("review")
#     game_to_update = db.session.get(Game, game_id_from_form)
#     game_to_update.rating = request.form.get("rating")
#
#     if not new_review == "":
#         game_to_update.review = new_review
#     else:
#         print("GAME IS IS NULL")
#     db.session.commit()

### REQUEST GAMES
def get_games_list_data(search_value):
    game_list = []
    params = {
        "key": "e8d6883d38f94755a3e56cdead8e9544",
        "search": search_value
    }

    response_game = requests.get("https://api.rawg.io/api/games", params=params)
    games_response = response_game.json()

    for game in games_response["results"]:
        game_list.append(game)
    return game_list


### SHORTEN DESCRIPTION
def cut_paragraph(text):
    cutoff = 250
    end_position = text.rfind('.', 0, cutoff)

    if end_position == -1:
        shortened_text = text[:250]
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
new_game = Game(
    title="Euro Truck Simulator 2",
    year=2012,
    rating=9.5,
    review="I let my girlfriend have a try at this game, she started growing chest hair.",
    description="Travel across Europe as king of the road, a trucker who delivers important cargo across impressive"
                " distances! With dozens of cities to explore, your endurance, skill and speed will all be pushed to"
                " their limits. If you've got what it takes to be part of an elite trucking force, get behind the wheel"
                " and prove it!",
    img_url="https://upload.wikimedia.org/wikipedia/en/0/0e/Euro_Truck_Simulator_2_cover.jpg"
)
# Here we commit the changes
# with app.app_context():
#     db.session.add(new_game)
#     db.session.commit()

###########################
# WEBSITE ROUTES
###########################
@app.route('/')
def home():
    all_games = db.session.query(Game).order_by(Game.rating).all()
    for i in range(len(all_games)):
        all_games[i].ranking = len(all_games) - i
    return render_template("index.html", all_games=all_games)


@app.route('/edit/<int:game_id>', methods=["GET", "POST"])
def update(game_id):
    game_id = game_id
    game = Game.query.get(game_id)
    game_form = GameEditFull(
        title=game.title,
        year=game.year,
        rating=game.rating,
        review=game.review,
        description=game.description,
    )

    if game_form.validate_on_submit():
        # validate_update()
        game.title = game_form.title.data
        game.year = game_form.year.data
        game.rating = game_form.rating.data
        game.review = game_form.review.data
        game.description = game_form.description.data
        db.session.commit()

        return redirect(location=url_for('home'))

    game_id = request.form.get("game_id") or game_id
    game_to_update = db.session.get(Game, game_id)
    return render_template("update.html", form=game_form, game_to_update=game_to_update, game=game)


@app.route("/delete")
def delete():
    game_id = request.args.get("game_id")
    game_to_del = db.session.get(Game, game_id)

    db.session.delete(game_to_del)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add-game", methods=["GET", "POST"])
def add_game():
    form = AddGameForm()
    all_games = db.session.query(Game).all()
    if form.validate_on_submit():
        game_name = request.form.get("game_name")
        game_results = get_games_list_data(game_name)
        print(game_results)
    else:
        game_results = []
    return render_template("add_game.html", form=form, game_results=game_results, all_games=all_games)


@app.route("/get_game")
def get_game():
    game_id = request.args.get("game_id")
    params = {
        "key": "e8d6883d38f94755a3e56cdead8e9544",
    }
    response = requests.get(f"https://api.rawg.io/api/games/{game_id}", params=params)

    game_data = response.json()
    print(game_data)

    game_name = game_data["name"]
    game_description = cut_paragraph(game_data["description_raw"])
    release_date = get_year(game_data["released"])
    img_background = game_data["background_image"]

    with app.app_context():
        existing_game = Game.query.filter_by(title=game_name).first()

        if existing_game:
            return redirect(url_for("update", game_id=existing_game.id))

    game = Game(
        rating=0,
        review="None",
        title=game_name,
        year=release_date,
        description=game_description,
        img_url=img_background,
    )

    with app.app_context():
        db.session.add(game)
        db.session.commit()
        db.session.refresh(game)
    return redirect(url_for('update', game_id=game.id))


###########################
# RUN AND DEBUG SERVER
###########################
if __name__ == "__main__":
    app.run(debug=True)

