from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    cards = [
        {
            'image': 'images/image1.jpg',  # Only specify the path relative to the 'static' folder
            'name': 'Highlands',
            'location': 'Scotland',
            'description': 'The mountains are calling'
        },
        {
            'image': 'images/image2.jpg',
            'name': 'Machu Picchu',
            'location': 'Peru',
            'description': 'Adventure is never far away'
        },
        {
            'image': 'images/image3.jpg',
            'name': 'Chamonix',
            'location': 'France',
            'description': 'Let your dreams come true'
        }
    ]
    return render_template('index.html', cards=cards)

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_flask()
