from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g, session, request
from app import db
from app.models import *
from flask_login import login_user, login_required, logout_user, current_user
from app.utils import  *

# Define the Blueprint
main = Blueprint('main', __name__)

@main.before_request
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


# Home Route
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/tasks')
def task_list():
    page = request.args.get('page', 1, type=int)  # Get current page, default to 1
    per_page = 10  # Number of tasks per page

    # Fetch tasks ordered by `created_at` descending and paginate
    tasks = AnnotationTask.query.order_by(AnnotationTask.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'task_list.html',
        tasks=tasks.items,  # Paginated tasks for the current page
        page=tasks.page,
        total_pages=tasks.pages
    )

import os
# Annotation Page Route
@main.route('/annotation/<int:task_id>')
@login_required
def annotation_page(task_id):
    task = AnnotationTask.query.get(task_id)
    if task:
        return render_template('annotation.html', task=task)
    flash('Task not found!', 'danger')
    return redirect(url_for('main.index'))

@main.route('/submit', methods=['POST'])
@login_required
def submit_annotation():
    try:
        # Retrieve data from the form
        task_id = request.form.get('task_id')
        annotations_data = request.form.get('annotations_data')  # JSON with annotations
        screenshot_data = request.form.get('screenshot_data')  # Base64 encoded image

        print(f"Received task_id: {task_id}")
        print(f"Received annotations_data: {annotations_data}")
        print(f"Received screenshot_data: {bool(screenshot_data)}")  # Only checks if screenshot_data exists

        if not task_id or not annotations_data or not screenshot_data:
            print("Validation failed: Missing required fields.")
            raise ValueError("Missing task_id, annotations_data, or screenshot_data in the request.")

        # Parse the annotations
        try:
            annotations = json.loads(annotations_data)  # Parse annotation data
            print(f"Parsed annotations: {annotations}")
        except json.JSONDecodeError as e:
            print(f"Error decoding annotations JSON: {e}")
            raise ValueError(f"Error decoding annotations JSON: {e}")

        # Find the annotation task
        task = AnnotationTask.query.get_or_404(task_id)
        print(f"Found task: {task}")

        # Ensure the directory exists for storing screenshots inside static
        screenshot_upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'screenshots', f'task{task_id}')
        os.makedirs(screenshot_upload_dir, exist_ok=True)
        print(f"Screenshot upload directory: {screenshot_upload_dir}")

        # Save the screenshot (base64 image)
        try:
            screenshot_data = screenshot_data.split(',')[1]  # Remove the "data:image/jpeg;base64," prefix
            screenshot_bytes = base64.b64decode(screenshot_data)  # Decode the base64 image
            screenshot_filename = f"{task_id}_screenshot.jpg"  # Updated to .jpg format
            screenshot_path = os.path.join('uploads', 'screenshots', f'task{task_id}', screenshot_filename)

            # Save the screenshot using the full path under static
            with open(os.path.join(current_app.root_path, 'static', screenshot_path), 'wb') as f:
                f.write(screenshot_bytes)
            print(f"Screenshot saved to: {screenshot_path}")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            raise ValueError(f"Error saving screenshot: {e}")

        # Process and store annotations in the database
        for annotation in annotations:
            # Extract annotation details
            annotation_label = annotation.get('label', 'Unnamed')  # Default label
            x, y, width, height = annotation.get('x'), annotation.get('y'), annotation.get('width'), annotation.get('height')
            print(f"Processing annotation: label={annotation_label}, x={x}, y={y}, width={width}, height={height}")

            # Save the annotation submission
            new_submission = AnnotationSubmission(
                task_id=task.id,
                user_id=current_user.id,
                label=annotation_label,  # Label from annotation data
                x=x, y=y, width=width, height=height,  # Store bounding box details
                mask_path=screenshot_path  # Relative path to the saved screenshot
            )
            db.session.add(new_submission)

        db.session.commit()
        print("All annotations saved successfully.")

        # Notify admins about the submission
        notify_admin_on_submission(task)  # Define this function elsewhere
        print("Admin notified of the submission.")

        # Redirect to the task list after successful submission
        flash("Annotation submitted successfully.", "success")
        return redirect(url_for('main.task_list'))
    
    except Exception as e:
        print(f"Error occurred during annotation submission: {e}")
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500



# Error Handling Routes
@main.app_errorhandler(404)
def not_found_error(error):
    flash('The requested page was not found.', 'warning') 
    return render_template('errors/404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again later.', 'danger')  
    return render_template('errors/500.html'), 500

@main.route('/notifications')
@login_required
def notifications():
    # Get all notifications for the current user
    notifications = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.timestamp.desc()).all()

    # Mark all notifications as read
    for notification in notifications:
        if not notification.read:
            notification.read = True
    db.session.commit()

    return render_template('notifications.html', notifications=notifications)


@main.route('/notifications/read/<int:notification_id>')
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.recipient_id == current_user.id:
        notification.read = True
        db.session.commit()
    return redirect(url_for('notifications'))


from flask import render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import json

import os

@main.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    # Fetch the task details
    task = AnnotationTask.query.get_or_404(task_id)

    # Fetch all submissions for the task (by all users)
    submissions = AnnotationSubmission.query.filter_by(task_id=task.id).all()

    # Debugging: Log submissions and replace backslashes with forward slashes
    print(f"\nTask Submissions (Task ID: {task.id}):")
    for submission in submissions:
        # Replace backslashes with forward slashes
        submission.mask_path = submission.mask_path.replace("\\", "/")
        print(f"- User: {submission.user_id}, Label: {submission.label}, Mask Path: {submission.mask_path}")
    
    # Pass the details to the template
    return render_template(
        'user-task_detail.html', 
        task=task, 
        submissions=submissions, 
        project=task.project
    )

@main.route('/review/<int:review_id>', methods=['GET'])
@login_required
def view_review(review_id):
    # Fetch the review
    review = SubmissionReview.query.get_or_404(review_id)
    
    # Ensure the logged-in user is the recipient of the review
    if review.submission.user_id != current_user.id:
        flash('You do not have permission to view this review.', 'danger')
        return redirect(url_for('main.home'))

    # Fetch the associated submission
    submission = review.submission

    # Replace backslashes with forward slashes in the mask_path
    if submission.mask_path:
        submission.mask_path = submission.mask_path.replace("\\", "/")
        print(f"Debug: Final Mask Path: {submission.mask_path}")  # Debugging log

    return render_template(
        'view_review.html',
        review=review,
        submission=submission
    )

