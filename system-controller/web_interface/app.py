import os
from flask import Flask, render_template, url_for

# Ensure you're using the correct absolute path for your static files
project_root = os.path.abspath(os.path.dirname(__file__))  # The root directory of the project

app = Flask(__name__, static_folder=os.path.join(project_root, 'web_interface', 'static'))

IMAGE_FOLDER = os.path.join(project_root, 'web_interface', 'static', 'images')

@app.route('/')
def home():
    patient_data = {}

    try:
        for patient_folder in os.listdir(IMAGE_FOLDER):
            patient_folder_path = os.path.join(IMAGE_FOLDER, patient_folder)

            if os.path.isdir(patient_folder_path):  
                images = [f for f in os.listdir(patient_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                patient_data[patient_folder] = images
    except FileNotFoundError:
        patient_data = {}

    return render_template('home.html', patient_data=patient_data)

@app.route('/3d-view/<patient_id>')
def three_d_view(patient_id):
    patient_folder_path = os.path.join(IMAGE_FOLDER, patient_id)
    images = [url_for('static', filename=os.path.join('images', patient_id, f)) for f in os.listdir(patient_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    return render_template('3d-view.html', images=images, patient_id=patient_id)

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5050)

if __name__ == '__main__':
    start_flask()