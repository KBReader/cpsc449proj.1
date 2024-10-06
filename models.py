from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Parent/Base class for the models
class Base(DeclarativeBase):
  pass

# Initalize and setup connection to database
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # Explicit table name
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    admin: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    __tablename__ = 'movies'  # Explicit table name
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    description: Mapped[str] = mapped_column(db.Text)

    ratings = relationship('Rating', back_populates='movie')

class Rating(db.Model):
    __tablename__ = 'ratings'  # Explicit table name
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    score: Mapped[int] = mapped_column(db.Integer, nullable=False)
    
    # Foreign keys for relationships
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    
    user = relationship('User', back_populates='ratings')
    movie = relationship('Movie', back_populates='ratings')

class File(db.Model):
    __tablename__ = 'files'  # Explicit table name
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(db.String, nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='files')

# Adding a back reference to the User class for files
User.files = relationship('File', back_populates='user')
User.ratings = relationship('Rating', back_populates='user')

def initialize_database(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()

    #db.session.add(User(username="examples", admin=True))
    # db.session.commit()

    # users = db.session.execute(db.select(User)).scalars()

# @app.route('/check_db', methods=['POST'])
# def check_db_connection():
#     try:
#         # Establish a connection and execute a simple query using the connection
#         with db.engine.connect() as connection:
#             connection.execute(text('SELECT 1'))
#         return "PostgreSQL connection is working."
#     except OperationalError:
#         return "Failed to connect to PostgreSQL."

if __name__ == '__main__':
    app.run(debug=True)