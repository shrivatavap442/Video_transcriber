from flask import Flask, render_template, request
import whisper
import os
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TRANSCRIPT_FOLDER'] = 'transcriptions'

print("Loading Whisper model...")
model = whisper.load_model("tiny")

# Ensure folders exist
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

    # Convert video to audio using ffmpeg
    audio_path = filepath.rsplit('.', 1)[0] + ".mp3"
    command = f"ffmpeg -i \"{filepath}\" -vn -acodec libmp3lame \"{audio_path}\""
    subprocess.run(command, shell=True, check=True)

    # Transcribe
    result = model.transcribe(audio_path)
    transcription = result["text"]

    # Save transcription
    transcript_path = os.path.join(app.config['TRANSCRIPT_FOLDER'], file.filename + ".txt")
    with open(transcript_path, "w") as f:
        f.write(transcription)

    return render_template("index.html", transcription=transcription)

if __name__ == '__main__':
    app.run(debug=True)
