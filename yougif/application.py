from urlparse import urlparse, parse_qs
from werkzeug import secure_filename

import Image

import os
import subprocess

class YouGIF:
    @classmethod
    def download_movie(this, movie_url, session_id):
        """ Downloads a video from YouTube and splits it into frames.
        Returns True if success, False otherwise. """
        movie_id = this.extract_movie_id(movie_url)
        if not movie_id:
            return False

        # TODO: handle failures.
        subprocess.call('youtube-dl -f 5 -o tmp/%s/%s.flv %s' % (session_id, movie_id, movie_url), shell=True)
        subprocess.call('ffmpeg -i tmp/%s/%s.flv -r 15 -y -an -t 10 tmp/%s/out-%%3d.gif' % (session_id, movie_id, session_id), shell=True)

        return True

    @staticmethod
    def get_frames(session_id):
        num_frames = int(subprocess.check_output("ls tmp/%s | wc -l" % session_id, shell=True)) - 1
        return ["tmp/%s/out-%03d.gif" % (session_id, num) for num in xrange(1, num_frames)]

    @staticmethod
    def generate_gif(session_id, editor_data):
        ratio = editor_data['ratio']
        for image_data in editor_data['images']:
            name = secure_filename(image_data['name'])
            original_image = Image.open('tmp/%s/%s' % (session_id, name))

            for frame, attrs in image_data.items():
                if frame == 'name':
                    continue

                image_name = 'tmp/%s/out-%03d.gif' % (session_id, int(frame))
                base_image = Image.open(image_name).convert('RGBA')
                added_image = original_image.copy()
                
                # Apply resizing.
                added_image = added_image.resize(int(attrs['width'] * ratio),
                                                 int(attrs['height'] * ratio))

                # Apply rotation.
                if attrs.get('rotation'):
                    deg = int(attrs['rotation'])
                    deg = 360 - deg if (deg > 0) else deg * -1
                    added_image = added_image.rotate(deg)

                base_image.paste(added_image,
                                 int(attrs['left'] * ratio),
                                 int(attrs['right'] * ratio),
                                 mask=added_image)
                base_image.save(image_name)

        try:
            os.mkdir('output/%s' % session_id)
        except:
            pass

        subprocess.call('convert -delay 1x15 -loop 0 tmp/%s/out-*.gif -layers Optimize output/%s/final.gif' % (session_id, session_id), shell=True)
        return 'final.gif'

    @staticmethod
    def extract_movie_id(url):
        """ Parses a URL to extract the youtube video id. Returns the id as a
        string, or None. """
        # TODO: handle youtu.be urls.
        query = urlparse(url).query
        movie_id = parse_qs(query)['v'][0]
        return movie_id
