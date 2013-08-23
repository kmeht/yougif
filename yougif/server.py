import uuid
import json

from flask import Flask, url_for, request, render_template, send_from_directory, redirect
from werkzeug import secure_filename

from application import YouGIF

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        session_id = str(uuid.uuid4()).replace('-', '')
        YouGIF.download_movie(request.form['url'], session_id)
        return redirect(url_for('editor', session_id=session_id))

@app.route('/<session_id>', methods=['GET', 'POST'])
def editor(session_id):
    if request.method == 'GET':
        frames = YouGIF.get_frames(session_id)
        return render_template('editor.html', frames=frames)
    if request.method == 'POST':
        filename = YouGIF.generate_gif(session_id, request.json)
        return url_for('finish', session_id=session_id)

@app.route('/<session_id>/gif', methods=['GET'])
def finish(session_id):
    return send_from_directory('output/%s/' % session_id, 'final.gif')

@app.route('/tmp/<session_id>/<path:filename>')
def file_upload(session_id, filename):
    return send_from_directory('tmp/%s/' % session_id, filename)

@app.route('/<session_id>/add_image/<filename>', methods=['POST'])
def add_image(session_id, filename):
    filename = secure_filename(filename)
    image_data = YouGIF.add_image(session_id, request.data, filename)

    image_data['url'] = url_for('file_upload',
                                session_id=session_id,
                                filename=filename)
    return json.dumps(image_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)
