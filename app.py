from io import BytesIO
from flask import Flask, render_template, request, redirect, send_file
import requests
import os

app = Flask(__name__)

URL = 'https://myimageapi-331c302c2fab.herokuapp.com/'

S3_URL = 'https://image-api-bucket-2024.s3.eu-west-3.amazonaws.com'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        files = [('file', (file.filename, open(filepath, 'rb'), 'image/jpeg'))]
        response = requests.post(url=URL+'/images', files=files)
        image_name = response.json()['filename'].split("/")[1]
        return redirect(f'/image/{image_name}')
    response = requests.get(url=URL+'/images')
    images = response.json()['data']
    return render_template('index.jinja', S3_URL=S3_URL, images=images)


@app.route('/image/<image_name>')
def image(image_name):
    return render_template('image.jinja', image_name=image_name)


@app.route('/resize', methods=['POST'])
def resize():
    if request.method == 'POST':
        data = {'filename': request.form['filename'], 'width': request.form['width'], 'height': request.form['height']}
        response = requests.post(url=URL+'/actions/resize', json=data, headers={'Content-Type': 'application/json'})
        return send_file(BytesIO(response.content), mimetype='image/jpeg', as_attachment=True,
                         download_name=f'resized_{request.form["filename"]}')
