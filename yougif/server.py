import subprocess
import re
import uuid
import logging
import json
import os
import Image
import math

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
    if request.method == 'POST':
        bin_image = request.data

        name = filename

        with open("tmp/%s/%s" % (session_id, secure_filename(name)), "wb") as f:
            f.write(bin_image)
        
        img = Image.open("tmp/%s/%s" % (session_id, secure_filename(name)))
        width, height = img.size
        
        return_json = {}
        return_json['name'] = name
        return_json['url'] = url_for("file_upload", session_id=session_id, filename=secure_filename(name))
        return_json['height'] = height
        return_json['width'] = width
        
        return json.dumps(return_json)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=3001,debug=True)
