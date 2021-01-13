from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserAddForm(FlaskForm):
    """Form for adding users"""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=8)])


class LoginForm(FlaskForm):
    """Form for user to log in"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8)])


class JournalSiteForm(FlaskForm):
    """Form to add/edit dive journal site."""

    description = TextAreaField(
        "Description (public)",
        validators=[Optional()],
        render_kw={"placeholder": "Share your experience with other users", 'rows': 3},
    )
    notes = TextAreaField(
        "Notes (private)",
        validators=[Optional()],
        render_kw={"placeholder": "Just for you, notes will remain private", 'rows': 3},
    )
    rating = SelectField(
        "Rating",
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
        validators=[DataRequired()],
    )
