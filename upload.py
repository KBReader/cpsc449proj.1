from flask import Flask,request,jsonify
import os


@app.route('./upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        return jsonify({'message': 'File does not exist'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'File is not selected'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return jsonify({'message': 'File '{file.filename}' uploaded successfully!'}), 200

if __name__ == '__main__':
    app.run(debug = True)
