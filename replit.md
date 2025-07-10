# Video to Text Transcription Application

## Overview

This is a Flask-based web application that converts video files to text transcriptions using OpenAI's Whisper model. The application extracts audio from video files and uses AI to generate accurate transcriptions with timestamps.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple server-side architecture built on Flask:

- **Frontend**: Bootstrap-based responsive web interface with drag-and-drop file upload
- **Backend**: Flask web server handling file upload, processing, and transcription
- **AI Processing**: OpenAI Whisper model for speech-to-text conversion
- **File Processing**: MoviePy for video-to-audio extraction
- **Storage**: Local file system for temporary file storage

## Key Components

### Web Server (Flask)
- Handles HTTP requests and responses
- Manages file uploads with security validation
- Serves the web interface and API endpoints
- Uses session management for user interactions

### File Processing Pipeline
1. **File Upload**: Accepts video files up to 500MB
2. **Validation**: Checks file extensions against allowed formats (mp4, avi, mov, mkv, wmv, flv, webm, m4v)
3. **Audio Extraction**: Uses MoviePy to extract audio from video files
4. **Transcription**: Processes audio through Whisper model
5. **Result Display**: Shows transcribed text with timestamps

### AI Integration
- Uses OpenAI Whisper "base" model for transcription
- Loads model at application startup for efficiency
- Supports GPU acceleration through PyTorch when available

### Frontend Interface
- Dark theme Bootstrap UI
- Drag-and-drop file upload area
- Real-time processing feedback
- Segmented transcription display with timestamps
- Responsive design for mobile compatibility

## Data Flow

1. User uploads video file through web interface
2. Server validates file type and size
3. File is temporarily stored in uploads folder
4. Audio is extracted from video using MoviePy
5. Audio file is processed by Whisper model
6. Transcription results are returned to user
7. Temporary files are cleaned up

## External Dependencies

### Core Libraries
- **Flask**: Web framework for HTTP handling
- **Whisper**: OpenAI's speech recognition model
- **MoviePy**: Video processing and audio extraction
- **PyTorch**: Deep learning framework for Whisper
- **Werkzeug**: WSGI utilities for file handling

### Frontend Dependencies
- **Bootstrap**: CSS framework with dark theme
- **Font Awesome**: Icon library
- **JavaScript**: For drag-and-drop functionality and UI interactions

### System Requirements
- Python 3.7+
- Sufficient disk space for temporary file storage
- Optional: CUDA-compatible GPU for faster processing

## Deployment Strategy

### Local Development
- Files stored in local `uploads/` and `transcriptions/` directories
- Environment variable `SESSION_SECRET` for Flask session security
- Debug logging enabled for development

### Production Considerations
- File size limits enforced (500MB max)
- Secure filename handling to prevent directory traversal
- Temporary file cleanup after processing
- Error handling for model loading and file processing failures

### Storage Architecture
- **uploads/**: Temporary storage for uploaded video files
- **transcriptions/**: Storage for generated transcription files
- **templates/**: HTML templates for web interface

The application is designed to be self-contained with minimal external service dependencies, making it suitable for local deployment or containerization.