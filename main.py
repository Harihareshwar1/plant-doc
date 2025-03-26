from flask import Flask, request, jsonify
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
import requests
load_dotenv()

app = Flask(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)
@app.route('/')
def home():
    return jsonify({'msg':'hello world'})
@app.route('/predict', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        app.logger.error('No file part in request.files')
        return jsonify({"error": "No file part"}), 400
    else:
        file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        return jsonify({"error": "No selected file"}), 400

    try:
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result.get('secure_url')
        if not image_url:
            return jsonify({"error": "Failed to get secure URL from Cloudinary"}), 500

        # Make a request to another API with the image_url
        another_api_url = "https://plant-doc-126783779377.us-central1.run.app/predict"
        response = requests.get(another_api_url, params={"image_url": image_url})

        if response.status_code != 200:
            return jsonify({"error": "Failed to call another API"}), response.status_code

        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == '__main__':
    app.run(port=8080,host="0.0.0.0",debug=True)
