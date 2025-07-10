import os
import logging
import whisper
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from moviepy.video.io.VideoFileClip import VideoFileClip
import torch

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configuration
UPLOAD_FOLDER = 'uploads'
TRANSCRIPTION_FOLDER = 'transcriptions'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTION_FOLDER, exist_ok=True)

# Load Whisper model at startup
logger.info("Loading Whisper model...")
try:
    whisper_model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    whisper_model = None

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video file using MoviePy."""
    try:
        logger.info(f"Extracting audio from {video_path}")
        video = VideoFileClip(video_path)
        
        # Extract audio and save as WAV
        audio = video.audio
        audio.write_audiofile(audio_path, verbose=False, logger=None)
        
        # Clean up
        audio.close()
        video.close()
        
        logger.info(f"Audio extracted successfully to {audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        return False

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper."""
    try:
        if whisper_model is None:
            raise Exception("Whisper model not loaded")
            
        logger.info(f"Transcribing audio from {audio_path}")
        result = whisper_model.transcribe(audio_path)
        
        logger.info("Transcription completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return None

def save_transcription(transcription_data, filename):
    """Save transcription to a text file with timestamps."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(filename)[0]
        transcription_filename = f"{base_filename}_{timestamp}.txt"
        transcription_path = os.path.join(TRANSCRIPTION_FOLDER, transcription_filename)
        
        with open(transcription_path, 'w', encoding='utf-8') as f:
            f.write(f"Transcription for: {filename}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            
            # Write full text
            f.write("FULL TRANSCRIPTION:\n")
            f.write(transcription_data['text'] + "\n\n")
            
            # Write segments with timestamps
            f.write("TIMESTAMPED SEGMENTS:\n")
            for segment in transcription_data.get('segments', []):
                start_time = f"{int(segment['start']//60):02d}:{int(segment['start']%60):02d}"
                end_time = f"{int(segment['end']//60):02d}:{int(segment['end']%60):02d}"
                f.write(f"[{start_time} - {end_time}] {segment['text'].strip()}\n")
        
        logger.info(f"Transcription saved to {transcription_path}")
        return transcription_filename
        
    except Exception as e:
        logger.error(f"Error saving transcription: {e}")
        return None

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and transcription."""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash(f'File type not supported. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 'error')
        return redirect(url_for('index'))
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(video_path)
        
        logger.info(f"File uploaded: {video_path}")
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio_path = temp_audio.name
        
        try:
            # Extract audio from video
            if not extract_audio_from_video(video_path, audio_path):
                flash('Failed to extract audio from video', 'error')
                return redirect(url_for('index'))
            
            # Transcribe audio
            transcription_result = transcribe_audio(audio_path)
            if transcription_result is None:
                flash('Failed to transcribe audio', 'error')
                return redirect(url_for('index'))
            
            # Save transcription
            transcription_filename = save_transcription(transcription_result, filename)
            if transcription_filename is None:
                flash('Failed to save transcription', 'error')
                return redirect(url_for('index'))
            
            # Success
            flash(f'Transcription completed successfully! Saved as {transcription_filename}', 'success')
            
            # Return results
            return render_template('index.html', 
                                 transcription=transcription_result['text'],
                                 segments=transcription_result.get('segments', []),
                                 filename=filename,
                                 transcription_file=transcription_filename)
            
        finally:
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.unlink(audio_path)
                
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'whisper_model_loaded': whisper_model is not None,
        'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
        'transcription_folder_exists': os.path.exists(TRANSCRIPTION_FOLDER)
    })

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
