import os

from flask import Blueprint, Flask, jsonify, request

from auth import admin_required, login_required
from models import Movie, Rating, User, db

app = Flask(__name__)
app.debug = True

movies_blueprint = Blueprint('movies', __name__)  # Define a Blueprint for movies

# Admin can post new movie to database
@movies_blueprint.route('/movies', methods=['POST'])
@admin_required
def add_movie():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if title == None:
        return jsonify({'message': 'Title is missing'}), 412

    if Movie.query.filter_by(title=title).first():
        return jsonify({'message': 'Movie already exists'}), 409

    new_movie = Movie(title=title, description=description)
    db.session.add(new_movie)
    db.session.commit()

    return jsonify({'message': 'Movie added successfully'}), 201

# Admin can delete movie's ratings from database
@movies_blueprint.route('/movies/ratings/<movie_id>', methods=['DELETE'])
@admin_required
def delete_movie_ratings(movie_id):
    ratings = Rating.query.filter_by(movie_id=movie_id)
    
    for rating in ratings:
        db.session.delete(rating)

    db.session.commit()

    return jsonify({'message': 'Movie ID deleted successfully'}), 200

# Delete user's own rating
@movies_blueprint.route('/ratings/<rating_id>', methods=['DELETE'])
@login_required
def delete_rating(rating_id, user_token):
    rating = Rating.query.get(rating_id)
    user = User.query.filter_by(username=user_token['username']).first()

    if not rating:
        return jsonify({'message': 'Rating ID not found'}), 404
    
    #make sure if the rating belongs to the current user
    if rating.user_id != user.id:
        return jsonify({'message': 'The rating with this ID was not posted by you'}), 403
    
    db.session.delete(rating)
    db.session.commit()
    return jsonify({'message': 'Rating ID deleted succesfully'}), 200

# Get all ratings from all movies
@movies_blueprint.route('/ratings', methods =['GET'])
@login_required
def fetchall_ratings(user_token):
    movies = db.session.scalars(db.select(Movie)).fetchall()
    ratings_dict = {}
    for movie in movies:
        ratings_dict[movie.title] = []
        ratings = Rating.query.filter_by(movie_id=movie.id)
        for rating in ratings:
            ratings_dict[movie.title].append(rating.to_dict())

    return jsonify(ratings_dict), 200

# Update user rating
@movies_blueprint.route('/ratings/<rating_id>', methods =['PUT'])
@login_required
def update_rating(rating_id, user_token):

    user = User.query.filter_by(username=user_token['username']).first()
    rating = Rating.query.get(rating_id)

    if not rating:
        return jsonify ({'message': 'Rating ID not found'}), 404
    
    if rating.user_id != user.id:
        return jsonify({'message': 'The rating with this ID was not posted by you'}), 403

    data = request.get_json() 
    score = data.get('score')
    comment = data.get('comment')
    if score is None and comment is None:
        return jsonify({'message': 'No valid data in has been passed to update rating'}), 400
    
    if score is not None:
        if score < 1 or score > 10:
            return jsonify({'message': 'Invalid score: must be between 1 to 10'}), 400
        rating.score = score
    
    if comment is not None:
        rating.comment = comment

    db.session.commit()
    return jsonify({'message': 'Rating ID has been updated'}), 201

# Get movie information including ratings
@movies_blueprint.route('/movies/ratings/<movie_id>', methods = ['GET'])
@login_required
def retrieve_aRate(movie_id, user_token):

    movie = Movie.query.get(movie_id)

    if not movie:
        return jsonify({'message': 'The movie is not found'}), 404

    ratings = Rating.query.filter_by(movie_id=movie_id)
    rating_list = [rating.to_dict() for rating in ratings]
    return jsonify({movie.title: rating_list}), 200

# Post a user rating for a movie
@movies_blueprint.route('/movies/ratings/<movie_id>', methods = ['POST'])
@login_required
def submit_rate(movie_id, user_token):

    user = User.query.filter_by(username=user_token['username']).first()
    if user.admin == True:
        return jsonify({'message': 'Admins are not allowed to post ratings'}), 401
    
    movie = Movie.query.filter_by(id=movie_id).first()
    if not movie:
        return jsonify({'message': 'The movie is not found'}), 404
    
    rating = Rating.query.filter_by(movie_id=movie_id, user_id=user.id).first()
    if rating:
        return jsonify({"message": "Rating already exists"}), 409
    
    data = request.get_json()
    score = data.get('score')
    comment = data.get('comment')

    if score is None or not (1 <= score <= 10):
        return jsonify({'message': 'Invalid score: must be between 1 to 10'}), 400    
    
    rating = Rating(
        score = score,
        comment = comment,
        movie_id = movie_id,
        user_id = user.id
    )
 
    db.session.add(rating)
    db.session.commit()

    return jsonify({'message': 'Rating posted successfully','rating': rating.to_dict()}), 201

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


if __name__ == '__main__':
    app.run(debug = True)
