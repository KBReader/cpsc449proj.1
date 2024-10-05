from flask import Flask,request,jsonify

app = Flask(__name__)
app.debug = True

@app.route('/movies', methods=['POST'])
@admin_required
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
@admin_required
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie ID not found'}), 404

    db.session.delete(movie)
    db.session.commit()

    return jsonify({'message': 'Movie ID deleted successfully'}), 200


@app.route('/admin/ratings/<rating_id>', methods=['DELETE'])
@admin_required
def delete_rating(rating_id):
    rating = Rating.query.get(rating_id)
    if not rating:
        return jsonify({'message': 'Rating ID not found'}), 404
    
    db.session.delete(rating)
    db.session.commit()
    
    return jsonify({'message': 'Rating ID deleted succesfully'}), 200

@app.route('/ratings/<rating_id>', methods=['DELETE'])
@login_required
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
@login_required
def fetchall_ratings():
    ratings = db.session.scalars(db.select(Rating)).all() #does .fetchall or .all works?
    rating_list = [rating.to_dict() for rating in ratings]
    return jsonify(rating_list)

@app.route('/ratings/<rating_id>', methods =['PUT'])
@login_required
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
