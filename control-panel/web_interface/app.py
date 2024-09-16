from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    cards = [
        {
            'image': 'images/image1.jpg',  # Only specify the path relative to the 'static' folder
            'name': 'Slide 1',
            'location': 'Captured at: 11:58:18 ',
            'description': 'Perform AI analysis on your data'
        },
        {
            'image': 'images/image2.jpg',
            'name': 'Slide 2',
            'location': 'Captured at: 11:58:18 ',
            'description': 'Perform AI analysis on your data'
        },
        {
            'image': 'images/image3.jpg',
            'name': 'Slide 3',
            'location': 'Captured at: 11:58:18 ',
            'description': 'Perform AI analysis on your data'
        }
    ]
    return render_template('index.html', cards=cards)

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_flask()
