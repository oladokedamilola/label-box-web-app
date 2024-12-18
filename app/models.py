from app import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')

    #relationship
    annotations = db.relationship(
        'AnnotationSubmission',
        back_populates='user',  # Consistent with AnnotationSubmission
        lazy=True
    )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'



class AnnotationSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('annotation_task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    mask_path = db.Column(db.String(255), nullable=False)  # Path to the segmentation mask or screenshot file
    x = db.Column(db.Float, nullable=True)  # Bounding box x-coordinate
    y = db.Column(db.Float, nullable=True)  # Bounding box y-coordinate
    width = db.Column(db.Float, nullable=True)  # Bounding box width
    height = db.Column(db.Float, nullable=True)  # Bounding box height
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    type = db.Column(db.String(50), nullable=False, default='screenshot')  # Default is segmentation type

    # Relationships
    user = db.relationship('User', back_populates='annotations')
    task = db.relationship('AnnotationTask', back_populates='submissions')
    reviews = db.relationship('SubmissionReview', back_populates='submission', lazy=True)

    def __repr__(self):
        return f"<AnnotationSubmission {self.id}>"


class SubmissionReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('annotation_submission.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Status of the review (Complete, Partially Complete, Not Complete)
    review_description = db.Column(db.String(500), nullable=True)  # Detailed description of the review
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationships
    submission = db.relationship('AnnotationSubmission', back_populates='reviews')
    admin = db.relationship('User')  # Admin who gave the review

    def __repr__(self):
        return f"<SubmissionReview {self.status} - {self.submission_id}>"


class AnnotationProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)  # Description for the project
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Admin of the project

    # One-to-many relationship: A project can have multiple tasks
    tasks = db.relationship('AnnotationTask', back_populates='project', lazy=True)

    def __repr__(self):
        return f"<AnnotationProject {self.name}>"


class AnnotationTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('annotation_project.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project = db.relationship('AnnotationProject', back_populates='tasks')
    submissions = db.relationship('AnnotationSubmission', back_populates='task')

    def __repr__(self):
        return f"<AnnotationTask {self.title}>"



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who will receive the notification
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who sent the notification
    task_id = db.Column(db.Integer, db.ForeignKey('annotation_task.id'), nullable=True)  # Associated task, if any
    message = db.Column(db.String(255), nullable=False)  # Message content
    read = db.Column(db.Boolean, default=False, nullable=False)  # Whether the notification has been read
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)  # When the notification was created

    # Relationship with User (recipient and sender)
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return f'<Notification {self.id} - {self.message}>'




