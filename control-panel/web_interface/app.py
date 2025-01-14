from flask import Flask, render_template
import os

app = Flask(__name__)

IMAGE_FOLDER = os.path.join('control-panel', 'web_interface', 'static', 'images')

@app.route('/')
def home():
    try:
        image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    except FileNotFoundError:
        image_files = []  
    
    images = list(enumerate(image_files, start=1))
    return render_template('home.html', images=images)

@app.route('/3d-view')
def three_d_view():
    try:
        images = [os.path.join('/static/images', f) for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    except FileNotFoundError:
        images = []  

    return render_template('3d-view.html', images=images)


def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_flask()
