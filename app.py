from flask import Flask, render_template, request, jsonify
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from config import config
from voice_providers import get_voice_provider
from video_generator import VideoGenerator
from utils import validate_input, cleanup_old_files
from monitoring import time_request, UsageTracker
from storage_manager import StorageManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global usage tracker
usage_tracker = UsageTracker()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'fonts'), exist_ok=True)
    
    # Initialize video generator
    video_gen = VideoGenerator(app.config)
    
    # Initialize storage manager
    storage_manager = StorageManager(
        output_folder=app.config['UPLOAD_FOLDER'],
        max_age_hours=24,
        max_storage_gb=5.0
    )
    
    # Start scheduled cleanup (every 6 hours)
    storage_manager.start_scheduled_cleanup(interval_hours=6)
    
    @app.route('/')
    def index():
        # Check provider availability
        available_providers = {}
        for provider_name in ['openai', 'elevenlabs', 'google', 'azure']:
            provider = get_voice_provider(provider_name, app.config)
            available_providers[provider_name] = provider.is_available() if provider else False
        
        return render_template('index.html', available_providers=available_providers)
    
    @app.route('/api/voices/<provider>')
    def get_voices(provider):
        voice_provider = get_voice_provider(provider, app.config)
        if not voice_provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        return jsonify({'voices': voice_provider.get_voice_list()})
    
    @app.route('/api/stats')
    def get_stats():
        return jsonify(usage_tracker.get_stats())
    
    @app.route('/api/storage')
    def get_storage_stats():
        return jsonify(storage_manager.get_storage_stats())
    
    @app.route('/api/cleanup', methods=['POST'])
    def manual_cleanup():
        try:
            result = storage_manager.smart_cleanup()
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/generate', methods=['POST'])
    @time_request
    def generate_video():
        start_time = datetime.now()
        
        try:
            # Validate input
            validation_error = validate_input(request.form, app.config)
            if validation_error:
                usage_tracker.track_request(success=False)
                return jsonify({'error': validation_error}), 400
            
            # Extract form data
            data = {
                'text': request.form.get('text', '').strip(),
                'title': request.form.get('title', '').strip(),
                'color_template': request.form.get('colorTemplate', 'purple_blue'),
                'title_font': request.form.get('titleFont', 'msyh'),
                'body_font': request.form.get('bodyFont', 'msyh'),
                'voice_provider': request.form.get('voiceProvider', 'openai'),
                'voice': request.form.get('voice', 'alloy'),
                'voice_speed': float(request.form.get('voiceSpeed', '1.0')),
                'voice_stability': float(request.form.get('voiceStability', '0.5'))
            }
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = secure_filename(f"{data['title']}_{timestamp}")
            
            # Generate video
            result = video_gen.generate_video(data, base_filename)
            
            # Track usage
            generation_time = (datetime.now() - start_time).total_seconds()
            usage_tracker.track_request(success=result['success'], generation_time=generation_time)
            
            if result['success']:
                # Cleanup old files (keep last 10)
                cleanup_old_files(app.config['UPLOAD_FOLDER'], keep_count=10)
                
                return jsonify({
                    'success': True,
                    'video_url': f'/static/outputs/{base_filename}.mp4'
                })
            else:
                return jsonify({'error': result['error']}), 500
                
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            usage_tracker.track_request(success=False)
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large'}), 413
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create app instance for gunicorn
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(env == 'development'))