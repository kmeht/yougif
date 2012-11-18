import subprocess
import re
import uuid
import logging
import json
import os

from flask import Flask, url_for, request, render_template, send_from_directory
from werkzeug import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get_movie")
def get_movie():
    session_id = uuid.uuid4()
    movie_url = request.args.get("url", "")
    if movie_url:
        movie_id = re.search(r"v=(\w+)", movie_url).group(1)
        # Grab the youtube video
        subprocess.call("youtube-dl -f 5 -o tmp/%s/%s.flv %s" % (session_id, movie_id, movie_url), shell=True)

        # Get the frames
        subprocess.call("ffmpeg -i tmp/%s/%s.flv -r 15 -y -an -t 10 tmp/%s/out-%%3d.gif" % (session_id, movie_id, session_id), shell=True)

        # Put the frames together
        os.mkdir("output/%s" % session_id)
        subprocess.call("convert -delay 1x15 -loop 0 tmp/%s/out-*.gif -layers Optimize output/%s/%s.gif" % (session_id, session_id, movie_id), shell=True)

        return render_template('get_movie.html', movie_id=movie_id, session_id=session_id)
    else:
        return '<form>Youtube url to download: <input type="text" name="url"><br><input type="submit" value="Go!"></form>'

@app.route('/output/<path:filename>')
def output_gif(filename):
    return send_from_directory("output/", filename)

@app.route('/<session_id>/<path:filename>')
def file_upload(session_id, filename):
    return send_from_directory("tmp/%s/" % session_id, filename)

@app.route('/<session_id>/add_image', methods=['POST'])
def add_image(session_id):
    if request.method == 'POST':
        data = request.json
        
        name = data['filename']
        bin_image = data['file']
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

@app.route('/<session_id>/finish', methods=['POST'])
def finish(session_id):
    return 1

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=3001,debug=True)
    #url_for('static', filename="test.png")
