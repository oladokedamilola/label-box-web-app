from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, PasswordField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Project Description', validators=[DataRequired()])
    submit = SubmitField('Create Project')


class TaskForm(FlaskForm):
    project_name = StringField('Project Name', render_kw={'readonly': True})  # Make it non-editable
    title = StringField('Task Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = FileField('Image Upload', validators=[DataRequired()])
    submit = SubmitField('Add Task')


