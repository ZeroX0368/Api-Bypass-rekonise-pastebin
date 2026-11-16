
from flask import Flask, jsonify, request
import requests
import re
import time

app = Flask(__name__)

def extract_paste_id(url):
    """Extract paste ID from Pastefy URL"""
    # Handle both full URLs and just the ID
    if url.startswith('https://pastefy.app/'):
        return url.split('/')[-1]
    elif url.startswith('pastefy.app/'):
        return url.split('/')[-1]
    else:
        # Assume it's just the ID
        return url

def get_pastefy_content(paste_id):
    """Fetch content from Pastefy API"""
    start_time = time.time()
    try:
        # Pastefy API endpoint for raw content
        api_url = f"https://pastefy.app/api/v2/paste/{paste_id}"
        
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        end_time = time.time()
        time_taken = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        return {
            'success': True,
            'content': data.get('content', ''),
            'title': data.get('title', '') or 'N/A',
            'language': data.get('language', '') or 'N/A',
            'created': data.get('created', '') or 'N/A',
            'paste_id': paste_id,
            'time_taken_ms': time_taken
        }
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        time_taken = round((end_time - start_time) * 1000, 2)
        return {
            'success': False,
            'error': f'Request failed: {str(e)}',
            'paste_id': paste_id,
            'time_taken_ms': time_taken
        }
    except Exception as e:
        end_time = time.time()
        time_taken = round((end_time - start_time) * 1000, 2)
        return {
            'success': False,
            'error': f'Error: {str(e)}',
            'paste_id': paste_id,
            'time_taken_ms': time_taken
        }

@app.route('/')
def home():
    return jsonify({
        'message': 'Pastefy API',
        'usage': {
            'endpoint': '/api/pastefy',
            'methods': ['GET', 'POST'],
            'parameters': {
                'url': 'Full Pastefy URL (e.g., https://pastefy.app/mFGLQfek)',
                'id': 'Just the paste ID (e.g., mFGLQfek)'
            },
            'examples': [
                '/api/pastefy?url=https://pastefy.app/mFGLQfek',
                '/api/pastefy?id=mFGLQfek'
            ]
        }
    })

@app.route('/api/pastefy', methods=['GET', 'POST'])
def get_paste():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        url = data.get('url')
        paste_id = data.get('id')
    else:
        url = request.args.get('url')
        paste_id = request.args.get('id')
    
    # Determine paste ID
    if url:
        paste_id = extract_paste_id(url)
    elif not paste_id:
        return jsonify({
            'success': False, 
            'error': 'Please provide either "url" or "id" parameter'
        }), 400
    
    # Validate paste ID format (basic validation)
    if not paste_id or len(paste_id) < 3:
        return jsonify({
            'success': False,
            'error': 'Invalid paste ID format'
        }), 400
    
    result = get_pastefy_content(paste_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404

@app.route('/api/pastefy/raw/<paste_id>')
def get_paste_raw(paste_id):
    """Get raw content only"""
    result = get_pastefy_content(paste_id)
    
    if result['success']:
        return result['content'], 200, {'Content-Type': 'text/plain'}
    else:
        return jsonify(result), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
