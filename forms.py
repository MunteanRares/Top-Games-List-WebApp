from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, validators
from wtforms.fields.simple import EmailField, TextAreaField


class AddGameForm(FlaskForm):
    game_name = StringField(label="Game Name", validators=[validators.DataRequired()], render_kw={"placeholder": "Enter a game title..."})
    submit = SubmitField(label="Search")

class GameEditFull(FlaskForm):
    title = StringField(label="Game Title", validators=[validators.DataRequired()])
    year = IntegerField(label="Game Year", validators=[validators.DataRequired()])
    rating = FloatField(label="Game Rating", validators=[validators.DataRequired()])
    review = StringField(label="Game Review", validators=[validators.DataRequired()])
    description = TextAreaField(label="Game Description")
    submit = SubmitField(label="Submit")

class RegisterForm(FlaskForm):
    name = StringField(label="Name", validators=[validators.DataRequired()], render_kw={"placeholder": "Enter your name"})
    email = EmailField(label="Email", validators=[validators.DataRequired(), validators.Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField(label="Password", validators=[validators.DataRequired()], render_kw={"placeholder": "Enter your password"})
    confirm_password = PasswordField(label="Confirm Password", validators=[validators.DataRequired()], render_kw={"placeholder": "Enter your password"})
    submit = SubmitField("Register Now")

class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[validators.DataRequired(), validators.Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField(label="Password", validators=[validators.DataRequired()], render_kw={"placeholder": "Enter your password"})
    submit = SubmitField("Log In")