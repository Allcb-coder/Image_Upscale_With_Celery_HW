from flask import Blueprint, request, jsonify, send_file
import io
import uuid
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'bmp'}

@bp.route('/')
def index():
    return jsonify({
        'service': 'EDSR Image Upscaler API',
        'endpoints': {
            'POST /upscale': 'Upload image for 2x upscaling',
            'GET /tasks/<task_id>': 'Check task status',
            'GET /processed/<task_id>': 'Download upscaled image'
        },
        'model': 'EDSR_x2 (TensorFlow) with OpenCV fallback'
    })

@bp.route('/upscale', methods=['POST'])
def upscale():
    """Upload image - NO DISK SAVING"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        # Read directly into memory - NO DISK
        image_bytes = file.read()

        # Start Celery task
        from app.tasks import upscale_image_task
        task = upscale_image_task.delay(image_bytes, file.filename)

        return jsonify({
            'task_id': task.id,
            'status': 'processing',
            'check_status': f'/tasks/{task.id}',
            'download': f'/processed/{task.id}'
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Check task status - CORRECT ROUTE"""
    from app.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'state': task.state,
    }

    if task.state == 'SUCCESS':
        result = task.result
        response['result'] = {
            'status': result.get('status'),
            'filename': result.get('filename'),
            'message': result.get('message')
        }
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)

    return jsonify(response)

@bp.route('/processed/<task_id>', methods=['GET'])
def get_processed(task_id):
    """Download upscaled image - CORRECT ROUTE, NO DISK"""
    try:
        from app.celery_app import celery_app

        task = celery_app.AsyncResult(task_id)

        if task.state != 'SUCCESS':
            return jsonify({
                'error': 'Task not completed',
                'state': task.state
            }), 404

        result = task.result
        if not isinstance(result, dict) or 'image_bytes' not in result:
            return jsonify({'error': 'Invalid result format'}), 500

        # Send bytes directly - NO DISK READ
        return send_file(
            io.BytesIO(result['image_bytes']),
            mimetype='image/png',
            as_attachment=True,
            download_name=result.get('filename', 'upscaled.png')
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500