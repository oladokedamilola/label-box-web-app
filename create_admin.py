from app import db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin(username, email, password):
    """
    Create an admin user in the database.

    Args:
        username (str): The admin's username.
        email (str): The admin's email.
        password (str): The admin's password.
    """
    # Check if admin already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f"User with email {email} already exists.")
        return

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create a new admin user
    admin = User(
        username=username,
        email=email,
        role='admin',
        password_hash=hashed_password  # Set the hashed password directly
    )

    # Add and commit the new admin user to the database
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user {username} created successfully.")

if __name__ == "__main__":
    # Set the admin credentials here
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    # Initialize the app context if necessary
    from app import create_app
    app = create_app()
    with app.app_context():
        create_admin(username, email, password)
