from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)

# Enviornmental Variable for password at the end
# set DB_PASSWORD=1234 in cmd
# password = os.getenv("DB_PASSWORD")
# Replace app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost/postgres"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:1234@localhost/postgres"

# Disables SQLAlchemy tracking (Reduces memory usage & improves performance)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Parent/Base class for the models
class Base(DeclarativeBase):
  pass

# Initalize and setup connection to database
db = SQLAlchemy(app, model_class=Base)

# Create tables for each
class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    admin: Mapped[bool] = mapped_column(db.Boolean, default=False)

class Movie(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    description: Mapped[str] = mapped_column(db.Text)

class Rating(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    score: Mapped[int] = mapped_column(db.Integer, nullable=False)
    
    # Foreign keys for relationships
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    

with app.app_context():
    db.create_all()

    #db.session.add(User(username="examples", admin=True))
    db.session.commit()

    # users = db.session.execute(db.select(User)).scalars()

@app.route('/check_db', methods=['POST'])
def check_db_connection():
    try:
        # Establish a connection and execute a simple query using the connection
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return "PostgreSQL connection is working."
    except OperationalError:
        return "Failed to connect to PostgreSQL."

if __name__ == '__main__':
    app.run(debug=True)