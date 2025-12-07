from flask import Flask, request, jsonify, send_file
from celery import Celery
import os
import uuid
import cv2
from werkzeug.utils import secure_filename

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp'}

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Create Celery app
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@celery.task(bind=True)
def upscale_task(self, input_path, output_filename):
    """Celery task to upscale image"""
    try:
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            return {'status': 'error', 'message': 'Could not read image'}

        # Get dimensions
        height, width = img.shape[:2]

        # Upscale 2x using OpenCV
        upscaled = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

        # Save result
        output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)
        cv2.imwrite(output_path, upscaled)

        # Clean up original
        os.remove(input_path)

        return {
            'status': 'success',
            'original_size': f'{width}x{height}',
            'upscaled_size': f'{width*2}x{height*2}',
            'output_file': output_filename
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/')
def home():
    return jsonify({
        'service': 'Image Upscaling API',
        'endpoints': {
            'POST /upscale': 'Upload image for upscaling',
            'GET /status/<task_id>': 'Check task status',
            'GET /download/<filename>': 'Download processed image'
        }
    })

@app.route('/upscale', methods=['POST'])
def upscale():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Generate unique filename
    original_ext = os.path.splitext(file.filename)[1]
    unique_id = uuid.uuid4().hex
    input_filename = f"{unique_id}_original{original_ext}"
    output_filename = f"{unique_id}_upscaled.jpg"

    # Save uploaded file
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(input_path)

    # Start Celery task
    task = upscale_task.delay(input_path, output_filename)

    return jsonify({
        'message': 'Image uploaded and upscaling started',
        'task_id': task.id,
        'status_url': f'/status/{task.id}',
        'download_url': f'/download/{output_filename}'
    }), 202

@app.route('/status/<task_id>')
def task_status(task_id):
    task = upscale_task.AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'state': task.state,
    }

    if task.state == 'SUCCESS':
        response['result'] = task.result
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)

    return jsonify(response)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['RESULT_FOLDER'], filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)