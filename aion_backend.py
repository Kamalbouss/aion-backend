#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
import io

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'videos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

generated_videos = {}

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/api/generate', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        lang = data.get('lang', 'ar')
        duration = int(data.get('duration', 30))
        style = data.get('style', 'kids')

        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        scene_count = max(1, duration // 5)
        video_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        generated_videos[video_id] = {
            'topic': topic,
            'lang': lang,
            'duration': duration,
            'style': style,
            'scenes': scene_count,
            'status': 'created',
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'video_id': video_id,
            'video_url': f'/api/download/{video_id}',
            'scenes': scene_count,
            'duration': duration,
            'message': f'تم إنشاء {scene_count} مشاهد بنجاح'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    try:
        if video_id not in generated_videos:
            return jsonify({'error': 'Video not found'}), 404

        dummy_video = b'RIFF' + b'\x00' * 100
        return send_file(
            io.BytesIO(dummy_video),
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'AION_{video_id}.mp4'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos', methods=['GET'])
def list_videos():
    return jsonify({
        'total': len(generated_videos),
        'videos': list(generated_videos.values())
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
