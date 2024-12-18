from flask import request, jsonify, flash, redirect, url_for, render_template, Blueprint, g, current_app
from flask_login import login_required
from app import db
from app.models import *
from .forms import TaskForm, ProjectForm
from flask_login import login_required, current_user
from app.utils import *
from werkzeug.utils import *
admin = Blueprint('admin', __name__)
import shutil


@admin.before_request
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



@admin.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Fetch all projects created by the admin
    projects = AnnotationProject.query.filter_by(admin_id=current_user.id).all()
    
    # Calculate the number of submissions for each project
    for project in projects:
        project.submissions_count = sum(
            [len(task.submissions) for task in project.tasks]
        )
    
    return render_template('admin/admin_dashboard.html', projects=projects)

  
@admin.route('/admin/project_list', methods=['GET'])
@admin_required
def project_list():
    # Get the page number from the request, default is 1
    page = request.args.get('page', 1, type=int)
    
    # Query projects, 10 per page
    projects = AnnotationProject.query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('admin/project_list.html', projects=projects)



@admin.route('/admin/project/<int:project_id>', methods=['GET'])
@admin_required
def project_detail(project_id):
    project = AnnotationProject.query.get_or_404(project_id)
    tasks = AnnotationTask.query.filter_by(project_id=project_id).all()

    if not tasks:
        print(f"Project Name: {project.name}, No tasks found.")
    else:
        # Generate the full image URL for each task
        for task in tasks:
            if task.image_url:
                # Extract the file name from the image_url
                file_name = os.path.basename(task.image_url)  # Extract the file name
                # Construct the correct path within the project's folder
                task.image_url = os.path.join('uploads', project.name, file_name).replace('\\', '/')
                print(f"Project Name: {project.name}, Task ID: {task.id}, Image Path: {task.image_url}")

    return render_template('admin/project_detail.html', project=project, tasks=tasks)



@admin.route('/task/<int:task_id>', methods=['GET'])
def task_detail(task_id):
    # Query the task using the provided `task_id`
    task = AnnotationTask.query.get_or_404(task_id)

    # Pass the task object to the template
    return render_template('admin/task_detail.html', task=task)

# Admin - Create Project Route
@admin.route('/admin/create_project', methods=['GET', 'POST'])
@admin_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = AnnotationProject(
            name=form.name.data,
            description=form.description.data,
            admin_id=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()

        # Create a folder for the new project inside the static/uploads folder
        project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], new_project.name)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)  # Create the project folder if it doesn't exist

        flash('Project created successfully!', 'success')
        return redirect(url_for('admin.add_task', project_id=new_project.id))  # Redirect to add task page
    return render_template('admin/create_project.html', form=form)

@admin.route('/admin/add_task/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def add_task(project_id):
    # Retrieve the project and its name
    project = AnnotationProject.query.get_or_404(project_id)
    project_name = project.name

    # Prepopulate the form with project name
    form = TaskForm()
    form.project_name.data = project_name  # Make the project name read-only in the form

    if form.validate_on_submit():
        # Initialize filename and image_url
        filename = None
        image_url = None

        # Create a new task instance (without committing yet)
        new_task = AnnotationTask(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
        )
        db.session.add(new_task)

        # Define the project folder path
        project_folder = os.path.join(
            current_app.root_path, 'static/uploads', project_name
        )
        os.makedirs(project_folder, exist_ok=True)  # Ensure project folder exists

        # Handle file upload if present
        if form.image_url.data:
            image_file = form.image_url.data
            filename = secure_filename(image_file.filename)

            # Define the full file path for the image
            filepath = os.path.join(project_folder, filename)
            image_file.save(filepath)  # Save the image file

            # Save the relative file path for static usage
            image_url = f'uploads/{project_name}/{filename}'.replace('\\', '/')

        # Update the task with the image URL (if any)
        new_task.image_url = image_url

        # Commit changes to the database
        db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('admin.project_detail', project_id=project_id))

    return render_template('admin/add_task.html', form=form, project_id=project_id, project_name=project_name)

@admin.route('/update_project/<int:project_id>', methods=['GET', 'POST'])
def update_project(project_id):
    project = AnnotationProject.query.get_or_404(project_id)
    form = ProjectForm()

    if form.validate_on_submit():
        project.title = form.name.data
        project.description = form.description.data
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin.project_detail', project_id=project.id))

    form.name.data = project.name
    form.description.data = project.description
    return render_template('admin/update_project.html', form=form, project=project)

@admin.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = AnnotationProject.query.get_or_404(project_id)

    # Handle annotation tasks associated with the project
    tasks = AnnotationTask.query.filter_by(project_id=project.id).all()
    for task in tasks:
        # You can either delete the tasks
        db.session.delete(task)

    db.session.commit()

    # Now delete the project
    db.session.delete(project)
    db.session.commit()

    # Delete project folder if it exists
    project_folder = os.path.join('path_to_project_folders', str(project.id))
    if os.path.exists(project_folder):
        shutil.rmtree(project_folder)

    flash('Project deleted successfully!', 'danger')
    return redirect(url_for('admin.project_list'))


# Admin - Update Task Route
@admin.route('/admin/update_task/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def update_task(task_id):
    # Get the task and associated project
    task = AnnotationTask.query.get_or_404(task_id)
    project_name = task.project.name if task.project else "Unknown_Project"  # Default if no project

    form = TaskForm(obj=task)
    form.project_name.data = project_name  # Prepopulate the project name

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data

        # Handle image upload
        if form.image_url.data:
            # Secure the filename
            image_file = form.image_url.data
            filename = secure_filename(image_file.filename)

            # Define the project folder path
            project_folder = os.path.join(
                current_app.root_path, 'static/uploads', project_name
            )
            os.makedirs(project_folder, exist_ok=True)  # Ensure the project folder exists

            # Save the image to the designated folder
            filepath = os.path.join(project_folder, filename)
            image_file.save(filepath)

            # Update the task's image URL (relative path for usage in templates)
            task.image_url = f'uploads/{project_name}/{filename}'

        # Commit changes to the database
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('admin.project_detail', project_id=task.project_id))

    return render_template('admin/update_task.html', form=form, task=task, task_id=task_id)

# Admin - Delete Task Route
@admin.route('/admin/task/delete/<int:task_id>', methods=['POST'])
@admin_required
def delete_task(task_id):
    task = AnnotationTask.query.get_or_404(task_id)
    try:
        # Remove the associated file if necessary
        if task.image_url:
            # Construct the full file path based on the relative image URL
            file_path = os.path.join(current_app.root_path, 'static', task.image_url)
            if os.path.exists(file_path):
                os.remove(file_path)  # Delete the image file

        # Delete the task from the database
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}', 'danger')

    return redirect(url_for('admin.project_detail', project_id=task.project_id))


# Admin - View Tasks Route
@admin.route('/admin/tasks', methods=['GET', 'POST'])
@admin_required
def manage_tasks():
    """
    Admin route to view tasks or review a specific task.
    - GET: Displays all tasks with their details.
    - POST: Updates the status of a specific task and notifies the annotator.
    """
    if request.method == 'GET':
        tasks = AnnotationTask.query.all()
        task_details = []
        for task in tasks:
            submissions = AnnotationSubmission.query.filter_by(task_id=task.id).all()
            task_data = {
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'image_url': task.image_url,
                'status': task.status,
                'submissions': [
                    {
                        'label': submission.label,
                        'coordinates': submission.coordinates,
                        'timestamp': submission.timestamp
                    }
                    for submission in submissions
                ]
            }
            task_details.append(task_data)
        return render_template('admin/view_tasks.html', task_details=task_details)

    elif request.method == 'POST':
        try:
            task_id = request.form.get('task_id')
            status = request.form.get('status')

            task = AnnotationTask.query.get(task_id)
            if not task:
                flash('Task not found!', 'danger')
                return jsonify({'error': 'Task not found'}), 404

            # Update task review status
            task.status = status
            db.session.commit()

            # Notify the annotator about the review status
            notify_annotator_on_review(task, status)

            flash(f"Task '{task.title}' has been {status}.", 'success')
            return jsonify({'message': f"Task '{task.title}' has been {status}."}), 200

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return jsonify({'error': 'An error occurred'}), 500


@admin.route('/admin/review_submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def review_submission(submission_id):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.home'))

    submission = AnnotationSubmission.query.get_or_404(submission_id)

    if request.method == 'POST':
        # Retrieve review details from the form
        status = request.form['status']
        review_description = request.form['review_description']

        # Create a new review entry
        review = SubmissionReview(
            submission_id=submission.id,
            admin_id=current_user.id,
            status=status,
            review_description=review_description
        )
        
        db.session.add(review)
        db.session.commit()

        # Notify the user about the review
        notify_user_of_review(submission.user, review)  # Notify user after review submission

        flash('Review submitted and notification sent to the user!', 'success')
        return redirect(url_for('main.task_detail', task_id=submission.task_id))

    # GET request: show the review form
    return render_template('admin/review_submission.html', submission=submission)
