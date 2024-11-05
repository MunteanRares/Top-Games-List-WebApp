from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField, FloatField, validators
from flask_wtf import FlaskForm

###########################
# CREATE APP SERVER
###########################
app = Flask(__name__)
app.secret_key = "aijsdoiasjoiada"

###########################
# CONNECT SQLALCHEMY TO DATABASE
###########################
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///game-database.db"
db = SQLAlchemy(app)


###########################
# CREATE CLASS FOR FORMS
###########################
class Form(FlaskForm):
    rating = FloatField(label="Your Rating",)
    review = StringField(label="Your Review", validators=[validators.length(max=75)])
    submit = SubmitField(label="Submit")

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
### Create to database.
with app.app_context():
    db.create_all()


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
# # Here we commit the changes
# with app.app_context():
#     db.session.add(new_game)
#     db.session.commit()


###########################
# WEBSITE ROUTES
###########################
@app.route('/')
def home():
    all_games = db.session.query(Game).all()
    return render_template("index.html", all_games=all_games)

@app.route('/edit', methods=["GET", "POST"])
def update():
    form = Form()
    game_id = request.args.get("id")
    game_to_update = db.session.get(Game, game_id)

    if form.validate_on_submit():
        game_id_from_form = request.form.get("id")
        new_review = request.form.get("review")

        game_to_update = db.session.get(Game, game_id_from_form)
        game_to_update.rating = request.form.get("rating")

        if not new_review == "":
            game_to_update.review = new_review
        else:
            print("GAME ID IS NULL")

        db.session.commit()
        return redirect(location=url_for('home'))
    return render_template("update.html", form=form, game_to_update=game_to_update)

@app.route("/delete")
def delete():
    game_id = request.args.get("id")
    game_to_del = db.session.get(Game, game_id)

    db.session.delete(game_to_del)
    db.session.commit()
    return redirect(url_for('home'))

###########################
# RUN AND DEBUG SERVER
###########################
if __name__ == "__main__":
    app.run(debug=True)

