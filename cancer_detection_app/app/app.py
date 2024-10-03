import os
import numpy as np
from flask import Flask, request, render_template, redirect, url_for
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageDraw

app = Flask(__name__)
model = load_model(r"C:\Users\akios\ScienceFair\cancer_detection_app\webapp\model\cancer_detection_model.h5")

classes = ['no_cancer', 'cancer']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)  

    img_path = os.path.join(uploads_dir, file.filename)
    file.save(img_path)

    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    print("Raw Prediction:", prediction)  
    class_idx = int(prediction[0][0] > 0.5)  
    class_name = classes[class_idx]

    draw_image = Image.open(img_path)
    draw = ImageDraw.Draw(draw_image)
    
    if class_name == 'cancer':
        width, height =draw_image.size
        x1 = np.random.randint(0, width - 50)
        y1 = np.random.randint(0, height - 50)
        x2 = x1 + 50
        y2 = y1 + 50
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

    highlight_path = os.path.join(uploads_dir, 'highlighted_' + file.filename)
    draw_image.save(highlight_path)

    return render_template('results.html', prediction=class_name, highlight_image='uploads/highlighted_' + file.filename)

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5000)
    
if __name__ == '__main__':
    app.run(debug=True)
