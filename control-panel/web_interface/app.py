from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/3d-view')
def three_d_view():
    images = [
        '/static/images/image1.jpg',
        '/static/images/image2.jpg',
        '/static/images/image3.jpg'
    ]
    return render_template('3d-view.html', images=images)

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_flask()
