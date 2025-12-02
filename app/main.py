from flask import Blueprint, request, jsonify, send_file, url_for, current_app
from werkzeug.utils import secure_filename
import uuid
import os
import asyncio
import aiofiles
import functools
import sys
import os

# Add parent directory to path to import celery_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

bp = Blueprint('main', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def async_view(f):
    """Decorator to run async functions in Flask views"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

@bp.route('/')
def index():
    """Home page"""
    return jsonify({
        'message': 'Image Upscale Service',
        'endpoints': {
            'POST /upscale': 'Upload image (returns task ID)',
            'GET /tasks/<task_id>': 'Check task status',
            'GET /processed/<filename>': 'Download processed image'
        }
    })

@bp.route('/upscale', methods=['POST'])
def upscale():  # REMOVED async decorator - this is synchronous
    """Upload image for upscaling"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'File type not allowed. Allowed: {current_app.config["ALLOWED_EXTENSIONS"]}'
        }), 400
    
    try:
        # Read file - SYNC version (no await)
        image_data = file.read()
        
        if len(image_data) == 0:
            return jsonify({'error': 'Empty file'}), 400
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Import Celery app
        from celery_app import upscale_image_task
        
        # Start Celery task
        task = upscale_image_task.apply_async(
            args=[image_data, secure_filename(file.filename)],
            task_id=task_id
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'processing',
            'status_url': url_for('main.task_status', task_id=task_id, _external=True),
            'message': 'Image uploaded. Processing started.'
        }), 202
        
    except Exception as e:
        print(f"Error in /upscale endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/tasks/<task_id>', methods=['GET'])
def task_status(task_id):
    """Get task status"""
    try:
        # Import Celery app
        from celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        response = {
            'task_id': task_id,
            'state': task.state
        }
        
        if task.state == 'PENDING':
            response['message'] = 'Task pending'
        elif task.state == 'PROCESSING':
            if task.info:
                response.update(task.info.get('meta', {}))
        elif task.state == 'SUCCESS':
            response['message'] = 'Task completed'
            response['result'] = task.result
            if task.result:
                response['processed_url'] = url_for(
                    'main.get_processed',
                    filename=task.result,
                    _external=True
                )
        elif task.state == 'FAILURE':
            response['message'] = 'Task failed'
            if task.info:
                response['error'] = str(task.info)
        
        return jsonify(response)
    except Exception as e:
        print(f"Error in /tasks endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/processed/<filename>', methods=['GET'])
@async_view
async def get_processed(filename):
    """Serve processed image"""
    try:
        if not filename or '..' in filename or '/' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        filepath = os.path.join(
            current_app.config['PROCESSED_FOLDER'],
            filename
        )
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Use aiofiles for async file reading
        async with aiofiles.open(filepath, 'rb') as f:
            content = await f.read()
        
        # Determine content type
        if filename.lower().endswith('.png'):
            mimetype = 'image/png'
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            mimetype = 'image/jpeg'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(
            filepath,
            mimetype=mimetype,
            as_attachment=False,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'image-upscale'})
