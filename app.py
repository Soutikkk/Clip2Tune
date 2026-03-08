import os
from flask import Flask, render_template, request, send_from_directory, jsonify
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Renders the main dashboard."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """Handles MP4 upload and conversion to MP3."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.mp4'):
        # Secure the filename and save the upload
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Define output path
        output_filename = filename.rsplit('.', 1)[0] + '.mp3'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        try:
            # Extract audio using MoviePy
            video_clip = VideoFileClip(input_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(output_path)
            
            # Close clips to free up resources
            audio_clip.close()
            video_clip.close()
            
            return jsonify({
                'success': True,
                'message': 'Conversion Successful!',
                'download_url': f'/download/{output_filename}',
                'filename': output_filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file format. Please upload an MP4 file.'}), 400

@app.route('/download/<filename>')
def download(filename):
    """Provides the converted MP3 file for download."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Run the Flask app
    print("MP4 to MP3 Converter app is running at http://127.0.0.1:5000")
    app.run(debug=True)
