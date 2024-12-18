from app import create_app, db
from app.models import AnnotationProject, AnnotationTask

# Create the Flask app context
app = create_app()

def delete_all_projects_and_tasks():
    with app.app_context():
        # Delete all tasks first (since tasks have a foreign key to projects)
        db.session.query(AnnotationTask).delete()

        # Delete all projects after deleting tasks
        db.session.query(AnnotationProject).delete()

        # Commit the changes to the database
        db.session.commit()

        print("All projects and tasks have been deleted.")

# Run the function to delete projects and tasks
if __name__ == "__main__":
    delete_all_projects_and_tasks()
