# Labelbox Web App

A web-based annotation tool for managing image annotation projects and tasks. This application streamlines the process of annotating, reviewing, and managing annotations with a user-friendly interface and robust backend features.

---

## Features

### General Features:
- **Image Annotation**: Annotate images directly in the browser with an intuitive interface.
- **Database Integration**: All annotation projects, tasks, and submissions are stored in a database, eliminating the need for local device storage.
- **Notifications**:
  - Admins are notified when a task is submitted.
  - Annotators are notified when their tasks are reviewed (approved/rejected).
- **Task Review**:
  - Admins can view, approve, or reject submitted tasks.
  - Detailed task information is available in collapsible dropdowns for ease of navigation.
- **User Roles**:
  - Different roles for admins and annotators with role-based access control.

### Admin-Specific Features:
- View all tasks with detailed submissions in an organized, styled list.
- Approve or reject tasks with an interactive dropdown for selecting review status.
- Notifications sent to annotators on task review.

### Responsive Design:
- Mobile-friendly and responsive layout.
- Includes collapsible dropdowns for task details for a clean and efficient UI.

---

## File Structure
```
labelbox-web-app/
├── app/                 # Flask app code (views, models, static, templates, etc.)
├── instance/            # Optional, for configs or instance data
├── migrations/          # Database migrations (if using Flask-Migrate)
├── requirements.txt     # Dependencies file
├── run.py               # Entry point for the app
├── wsgi.py              # WSGI file to serve the app
├── .env                 # Environment variables (optional)
├── README.md            # Project info (optional)
```

---

## Installation

Follow these steps to set up the project locally:

### Step 1: Clone the Repository
```bash
git clone git https://github.com/oladokedamilola/label-box-web-app.git
cd labelbox-web-app
```

### Step 2: Install Dependencies
Install all the required Python dependencies using:
```bash
pip install -r requirements.txt
```

### Step 3: Set Up the Database
Initialize and migrate the database with the following commands:
```bash
flask db init
flask db migrate
flask db upgrade
```

### Step 4: Run the App
Start the application with:
```bash
python run.py
```

---

## Usage

1. **Annotators**:
   - View assigned tasks.
   - Submit annotations through the browser.
   
2. **Admins**:
   - Review all submitted tasks.
   - Approve or reject tasks with real-time notifications sent to annotators.
   - Access task details and submissions with a collapsible view.

---

## Deployment

This application can be deployed on platforms such as **Heroku**, **AWS**, or **Docker**. Ensure the necessary environment variables and database configurations are set.

---

## Future Enhancements
- Integration with additional image annotation tools for advanced features.
- Exporting annotated data in formats like JSON or CSV.
- Multi-language support.

---
