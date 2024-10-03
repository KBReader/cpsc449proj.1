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
    
@app.route('/delete/<title>', methods=['DELETE'])
@admin_required
def delete_movie(title):
    movie = Movie.query.get(title)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404

    db.session.delete(movie)
    db.session.commit()

    return jsonify({'message': 'Movie deleted successfully'}), 200


