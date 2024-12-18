import sys
import os

# Add your project directory to the system path
project_home = '/home/joshdammy22/labelbox-web-app'
if project_home not in sys.path:
    sys.path.append(project_home)

# Activate the virtual environment
activate_this = '/home/joshdammy22/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Import the Flask app (app instance) from your application
from app import app as application
