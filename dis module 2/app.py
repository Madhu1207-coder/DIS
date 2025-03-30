from flask import Flask, request, jsonify, render_template
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No file part', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    # Perform encryption by swapping pixel values
    encrypted_image = encrypt_image(file)
    
    return jsonify({'encrypted_image': encrypted_image})

def encrypt_image(file):
    image = Image.open(file)
    data = np.array(image)

    # Simple encryption: swap red and blue channels
    data[..., [0, 2]] = data[..., [2, 0]]  # Swap Red and Blue channels
    encrypted_image = Image.fromarray(data)

    # Convert image to base64 string
    buffered = io.BytesIO()
    encrypted_image.save(buffered, format="PNG")
    encrypted_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return f"data:image/png;base64,{encrypted_image_base64}"

@app.route('/decrypt', methods=['POST'])
def decrypt_image():
    if 'image' not in request.files:
        return 'No file part', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    # Perform decryption by swapping pixel values back
    decrypted_image = decrypt_image_func(file)
    
    return jsonify({'decrypted_image': decrypted_image})

def decrypt_image_func(file):
    image = Image.open(file)
    data = np.array(image)

    # Decrypt: swap red and blue channels back
    data[..., [0, 2]] = data[..., [2, 0]]  # Swap Red and Blue channels back
    decrypted_image = Image.fromarray(data)

    # Convert image to base64 string
    buffered = io.BytesIO()
    decrypted_image.save(buffered, format="PNG")
    decrypted_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return f"data:image/png;base64,{decrypted_image_base64}"

if __name__ == '__main__':
    app.run(debug=True,use_reloader = False)
