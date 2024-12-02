from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, validators
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import EmailField, TextAreaField


class AddGameForm(FlaskForm):
    game_name = StringField(label="Game Name", validators=[validators.DataRequired()], render_kw={"placeholder": "Enter a game title..."})
    submit = SubmitField(label="Search")

class GameEditFull(FlaskForm):
    rating = FloatField(label="Game Rating", validators=[validators.DataRequired()])
    review = StringField(label="Game Review", validators=[validators.DataRequired()])
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

class CommentForm(FlaskForm):
    comment = TextAreaField(label="Write your Review", validators=[validators.DataRequired()], render_kw={"placeholder": "Share your thoughts about this game..."})
    rating = RadioField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[validators.InputRequired()], coerce=int)
    submit = SubmitField("Add Review")