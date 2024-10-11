from flask import Flask,request,jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.debug = True

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    admin: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    description: Mapped[str] = mapped_column(db.Text)

    ratings = relationship('Rating', back_populates='movie')

class Rating(db.Model):
    __tablename__ = 'ratings'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    score: Mapped[int] = mapped_column(db.Integer, nullable=False)
    
    # Foreign keys for relationships
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    
    user = relationship('User', back_populates='ratings')
    movie = relationship('Movie', back_populates='ratings')

@app.route('/movies', methods=['POST'])
# @admin_required
def add_movie():
    data = request.get_json()
    title = data.get('title')

    if Movie.query.filter_by(title=title).first():
        return jsonify({'message': 'Movie already exists'}), 409

    new_movie = Movie(title=title)
    db.session.add(new_movie)
    db.session.commit()

    return jsonify({'message': 'Movie added successfully'}), 201
    
@app.route('/movies/<movie_id>', methods=['DELETE'])
# @admin_required
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie ID not found'}), 404

    db.session.delete(movie)
    db.session.commit()

    return jsonify({'message': 'Movie ID deleted successfully'}), 200


@app.route('/admin/ratings/<rating_id>', methods=['DELETE'])
# @admin_required
def admindelete_rating(rating_id):
    rating = Rating.query.get(rating_id)
    if not rating:
        return jsonify({'message': 'Rating ID not found'}), 404
    
    db.session.delete(rating)
    db.session.commit()
    
    return jsonify({'message': 'Rating ID deleted succesfully'}), 200

@app.route('/ratings/<rating_id>', methods=['DELETE'])
# @login_required
def delete_rating(rating_id, user_id):
    rating = Rating.query.get(rating_id)
    user = User.query.get(user_id)

    if not rating:
        return jsonify({'message': 'Rating ID not found'}), 404
    
    #make sure if the rating belongs to the current user
    if rating.user_id != user_id:
        return jsonify({'message': 'The rating ID is not posted by you'}), 403
    
    de.session.delete(rating)
    db.session.commit()
    return jsonify({'message': 'Rating ID deleted succesfully'}), 200

# retrieves all ratings from all users
@app.route('/ratings', methods =['GET'])
# @login_required
def fetchall_ratings():
    ratings = db.session.scalars(db.select(Rating)).all() #does .fetchall or .all works?
    rating_list = [rating.to_dict() for rating in ratings]
    return jsonify(rating_list)

@app.route('/ratings/<rating_id>', methods =['PUT'])
# @login_required
def update_rating(rating_id):

    rating = Rating.query.get(rating_id)
    user_id = current_user.id

    if not rating:
        return jsonify ({'message': 'Rating ID not found'}), 404
    
    if rating.user_id != user_id:
        return jsonify({'message': 'The rating ID is not posted by you'}), 403

    data = request.get_json()
    new_draft = jsonify('draft')

    if new_draft is None:
        return jsonify({'message': 'There is nothing in your rating'}), 400
    
    rating.draft = new_draft #key to updating
    db.session.commit()
    return jsonify({'message': 'Rating ID has been updated'}), 200

@app.route('/movies/<movie_id>/ratings', methods = ['GET'])
# @login_required
def retrieve_aRate(movie_id):

    movie = Movie.query.get(movie_id)

    if not movie:
        return jsonify({'message': 'The movie is not found'}), 404

    rating = Rating.query.filer_by(movie_id = movie_id).all()
    rating_list = [rating.to_dict() for rating in ratings]
    return jsonify(rating_list), 200

@app.route('/movies/<movie_id>/ratings', methods=['POST'])
# @login_required
def submint_rate(movie_id):

    movie = Movie.query.get(movie_id)

    if not movie:
        return jsonify({'message': 'The movie is not found'}), 404
    
    data = request.get_json()
    score = data.get('score')
    comment = data.get('comment')

    if score is None or not (1 <= score <= 10):
        return jsonify({'message': 'Invalid score: must be between 1 to 10'}), 400

    # Corrected line
    rating = Rating(
        score=score,
        comment=comment,
        movie_id=movie_id,
        user_id=current_user.id
    )

    db.session.add(rating)
    db.session.commit()

    return jsonify({'message': 'Rating posted successfully', 'rating': rating.to_dict()}), 201


UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


if __name__== '__main__':
    app.run(debug = True)
