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
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("Your views about this", validators=[DataRequired()])
    submit = SubmitField("Comment")


class LostFoundForm(FlaskForm):
    choices = ["Lost", "Found"]
    user_choice = SelectField("Choose one", choices=choices, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    item_desc = CKEditorField(f"Tell something about the item , enter your desired way of contact", validators=[DataRequired()])
    submit = SubmitField("Post")


class GrievanceForm(FlaskForm):
    choices = ["Cleanliness", "Other"]
    user_choice = SelectField("Type of issue", choices=choices, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_no = StringField("Phone number")
    grievance = CKEditorField("Tell us about your issue", validators=[DataRequired()])
    submit = SubmitField("Post")


class CanteenForm(FlaskForm):
    name = StringField("Your name", validators=[DataRequired()])
    order = CKEditorField("Enter your order in the form 'quantity' x 'menu item name' ", validators=[DataRequired()])
    submit = SubmitField("Order")
