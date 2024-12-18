from app import db
from app.models import User, Notification, AnnotationSubmission
from flask_login import current_user
from functools import wraps
from flask import flash, redirect, url_for, current_app
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect to login page
        return f(*args, **kwargs)
    return decorated_function


def notify_admin_on_submission(task):
    """
    Notify all admins when a new annotation task is submitted.

    Args:
        task: The submitted annotation task object.
    """
    # Get the submission related to the task and the user who submitted it
    submission = AnnotationSubmission.query.filter_by(task_id=task.id).first()  # Get the first submission for the task
    
    if submission:
        # Get the user who submitted the task
        user = submission.user
        
        # Notify admins about the submission
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            notification = Notification(
                recipient_id=admin.id,
                sender_id=user.id,  # Use the user from the submission
                task_id=task.id,
                message=f"User {user.username} has submitted an annotation task: {task.title}"
            )
            db.session.add(notification)
        db.session.commit()
    else:
        print(f"No submission found for task {task.id}. Unable to notify admins.")


def notify_annotator_on_review(task, status):
    """
    Notify the annotator when their task is reviewed by an admin.

    Args:
        task: The reviewed annotation task object.
        status: The review status (e.g., 'approved' or 'rejected').
    """
    notification = Notification(
        recipient_id=task.user.id,  # The annotator
        sender_id=task.project.admin_id,  # The admin (assuming project has an admin)
        task_id=task.id,
        message=f"Your task '{task.title}' has been {status} by the admin."
    )
    db.session.add(notification)
    db.session.commit()

# Helper function to save the image from base64 data
def save_image_from_base64(base64_data, filename):
    # Decode the base64 image data
    image_data = base64.b64decode(base64_data.split(',')[1])
    image = Image.open(BytesIO(image_data))
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    image.save(file_path)
    return file_path


def notify_user_of_review(user, review):
    message = f"""
    <a href="{url_for('main.view_review', review_id=review.id)}">
        Your submission for task {review.submission.task.title} has been reviewed.
    </a>
    """
    notification = Notification(
        recipient_id=user.id,
        sender_id=review.admin_id,
        task_id=review.submission.task_id,
        message=message
    )
    db.session.add(notification)
    db.session.commit()

