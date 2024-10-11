import os
from flask import Flask
from auth import auth_blueprint
from models import initialize_database

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(12)

# Enviornmental Variable for password at the end
# set DB_PASSWORD=1234 in cmd
# password = os.getenv("DB_PASSWORD")
# Replace app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost/postgres"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:1234@localhost/postgres"

# Disables SQLAlchemy tracking (Reduces memory usage & improves performance)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.register_blueprint(auth_blueprint, url_prefix='/auth')

# Ensure the database is initialized before starting the app
if __name__ == '__main__':
    initialize_database(app)  # Initialize tables
    app.run(debug=True)  # Start the Flask app
