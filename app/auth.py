from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm  
from app.models import Notification
import os

auth = Blueprint('auth', __name__)

@auth.before_request
def before_request():
    if current_user.is_authenticated:
        # Fetch unread notifications count for the current user
        unread_notifications_count = Notification.query.filter_by(recipient_id=current_user.id, read=False).count()
        # Fetch read notifications count for the current user
        read_notifications_count = Notification.query.filter_by(recipient_id=current_user.id, read=True).count()
        
        # Store the counts in the global context (g)
        g.unread_notifications_count = unread_notifications_count
        g.read_notifications_count = read_notifications_count
    else:
        g.unread_notifications_count = 0
        g.read_notifications_count = 0



# Registration Route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# Login Route
# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and user.check_password(form.password.data):
#             login_user(user)
#             flash('Login successful', 'success')
#             return redirect(url_for('main.index'))
#         else:
#             flash('Invalid username or password', 'danger')
#     return render_template('auth/login.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Check if the form is valid and the user exists
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful', 'success')

            # Check if there is a 'next' parameter in the URL, and redirect accordingly
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))

        else:
            flash('Invalid username or password', 'danger')

    # If the form is not submitted or invalid, we render the login page
    return render_template('auth/login.html', form=form)

# Logout Route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@auth.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))  # Redirect non-users to the main page or another page
    
    # Fetch tasks that the current user has submitted for
    tasks = db.session.query(AnnotationTask).join(AnnotationSubmission).filter(AnnotationSubmission.user_id == current_user.id).all()

    # Debugging information to ensure image_url is correct
    for task in tasks:
        print(f"Debug: Task ID: {task.id}, Image URL: {task.image_url}")
    
    return render_template('auth/user_dashboard.html', tasks=tasks)
