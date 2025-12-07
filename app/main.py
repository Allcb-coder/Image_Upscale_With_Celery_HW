from flask import Blueprint, request, jsonify, send_file, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from .tasks import upscale_image_task

main_bp = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@main_bp.route('/')
def index():
    return jsonify({
        'service': 'Image Upscaling API',
        'endpoints': {
            '/upscale': 'POST - Upload image for upscaling',
            '/status/<task_id>': 'GET - Check task status',
            '/download/<filename>': 'GET - Download processed image'
        }
    })


@main_bp.route('/upscale', methods=['POST'])
def upscale():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Generate unique filename
    original_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{original_ext}"

    # Save uploaded file
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(upload_path)

    # Start Celery task
    task = upscale_image_task.delay(upload_path, unique_filename)

    return jsonify({
        'message': 'Upscaling started',
        'task_id': task.id,
        'status_url': f'/status/{task.id}',
        'original_filename': file.filename
    }), 202


@main_bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    from .celery_app import celery
    task = celery.AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'state': task.state,
    }

    if task.state == 'SUCCESS':
        response['result'] = task.result
        if 'result_filename' in task.result:
            response['download_url'] = f"/download/{task.result['result_filename']}"
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)

    return jsonify(response)


@main_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    result_path = os.path.join(current_app.config['RESULT_FOLDER'], filename)

    if not os.path.exists(result_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(result_path, as_attachment=True)