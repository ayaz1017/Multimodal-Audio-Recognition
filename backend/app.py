from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.api import create_api_blueprint
from routes.auth import auth_bp
from routes.patients import patient_bp
from models.audio_model import load_model
from models.database import ensure_db

app = Flask(__name__)
CORS(app)
is_vercel = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
default_upload_folder = (
    '/tmp/uploads'
    if is_vercel
    else os.path.join(os.path.dirname(__file__), 'uploads')
)
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', default_upload_folder)
ALLOWED_EXTENSIONS = {
    'wav',
    'mp3',
    'm4a',
    'ogg',
    'flac',
    'mp4',
    'avi',
    'mov',
    'mkv',
    'webm',
    'jpg',
    'jpeg',
    'png',
}
MAX_FILE_SIZE = 50 * 1024 * 1024  

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
try:
    model = load_model()
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Error loading model: {str(e)}")
    model = None
app.model = model
ensure_db()
api_bp = create_api_blueprint()
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(patient_bp, url_prefix='/api/patients')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': app.model is not None
    }), 200

@app.route('/', methods=['GET'])
def welcome():
    """Welcome endpoint"""
    return jsonify({
        'app': 'Multimodal Audio Recognition',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'verify': 'POST /api/auth/verify',
                'profile': 'GET /api/auth/profile'
            },
            'patients': {
                'create': 'POST /api/patients',
                'list': 'GET /api/patients',
                'get': 'GET /api/patients/<patient_id>',
                'update': 'PUT /api/patients/<patient_id>',
                'get_analysis': 'GET /api/patients/<patient_id>/analysis',
                'save_analysis': 'POST /api/patients/<patient_id>/analysis'
            },
            'recognition': {
                'audio': 'POST /api/recognize_audio',
                'video': 'POST /api/recognize_video',
                'multimodal': 'POST /api/recognize_multimodal'
            }
        }
    }), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

if __name__ == '__main__':
    print("Starting Multimodal Audio Recognition Server...")
    print("API available at http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)
