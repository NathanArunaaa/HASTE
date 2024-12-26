from flask import Flask, render_template, jsonify
import os

# Set the static folder to 'static' within the 'web_interface' directory
app = Flask(__name__, static_folder='static', static_url_path='/static')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the path to the current file (app.py)
IMAGE_DIR = os.path.join(BASE_DIR, "static", "images")  # Join with static/images

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/images")
def get_images():
    """Return a list of image file names in the directory."""
    if not os.path.exists(IMAGE_DIR):
        return f"Directory {IMAGE_DIR} does not exist", 500

    images = sorted(os.listdir(IMAGE_DIR))
    if not images:
        return f"No images found in {IMAGE_DIR}", 500

    image_urls = [f"/static/images/{image}" for image in images]
    return jsonify(image_urls)


def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_flask()
