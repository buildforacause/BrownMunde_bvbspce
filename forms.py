from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm
class CreateEventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Event Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Event Content", validators=[DataRequired()])
    submit = SubmitField("Create")


class RegisterForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("your views about the event", validators=[DataRequired()])
    submit = SubmitField("comment")


class LostFoundForm(FlaskForm):
    choices = ["lost", "found"]
    user_choice = SelectField("lost or found", choices=choices, validators=[DataRequired()])
    name = StringField("your name", validators=[DataRequired()])
    item_desc = CKEditorField(f"tell something about the item , enter your desired way of contact", validators=[DataRequired()])
    submit = SubmitField("Post")


class GrievanceForm(FlaskForm):
    choices = ["cleanliness", "other"]
    user_choice = SelectField("type of issue", choices=choices, validators=[DataRequired()])
    name = StringField("your name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    phone_no = StringField("phone number")
    grievance = CKEditorField("tell us about your issue", validators=[DataRequired()])
    submit = SubmitField("Post")


class CanteenForm(FlaskForm):
    name = StringField("your name", validators=[DataRequired()])
    order = CKEditorField("enter your order in the form 'quantity' x 'menu item name' ", validators=[DataRequired()])
    submit = SubmitField("Order")
