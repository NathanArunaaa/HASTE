import os

os.chdir("/home/system-controller/HASTE/system-controller/web_interface")

from flask import Flask, render_template, url_for

app = Flask(__name__) 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = "/home/system-controller/HASTE/system-controller/web_interface/static/images"

@app.route('/')
def home():
    print("Flask running in directory:", os.getcwd())  # Debugging
    print("Looking for images in:", IMAGE_FOLDER)  # Debugging

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
    
    if not os.path.exists(patient_folder_path): 
        return "Patient folder not found", 404
    
    images = [f"/static/images/{patient_id}/{f}" for f in os.listdir(patient_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    return render_template('3d-view.html', images=images, patient_id=patient_id)


def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5050, debug=False, use_reloader=False)
if __name__ == '__main__':
    start_flask()