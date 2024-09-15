from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)

    

if __name__ == '__main__':
    start_flask()
