import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Downloads folder create karne ke liye
DOWNLOAD_FOLDER = '/tmp' # Hosting sites par /tmp folder writable hota hai

@app.route('/')
def home():
    return "Backend is Running!"

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "URL missing"}), 400

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/video_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render/Railway automatically port assign karte hain
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
