from flask import Flask, render_template, request
import whisper
import os
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TRANSCRIPT_FOLDER'] = 'transcriptions'

# Use lighter model to avoid out-of-memory error on Render free tier
print("Loading Whisper model...")
model = whisper.load_model("tiny")  # <-- changed from 'base' to 'tiny'

# Make sure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TRANSCRIPT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No file uploaded", 400

    file = request.files['video']
    if file.filename == '':
        return "No file selected", 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Extract audio from video
    audio_path = filepath.rsplit('.', 1)[0] + ".mp3"
    video = VideoFileClip(filepath)
    video.audio.write_audiofile(audio_path)

    # Transcribe audio
    print("Transcribing...")
    result = model.transcribe(audio_path)
    transcription = result["text"]

    # Save transcription to file
    transcript_path = os.path.join(app.config['TRANSCRIPT_FOLDER'], file.filename + ".txt")
    with open(transcript_path, "w") as f:
        f.write(transcription)

    return render_template("index.html", transcription=transcription)

if __name__ == '__main__':
    app.run(debug=True)
