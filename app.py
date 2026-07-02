"""
FRIDAY - Screen Sharing Assistant
Flask Web Application

This file provides a Flask web server for the FRIDAY frontend.
It exposes API endpoints for chat and vision analysis.

What is Flask?
- Flask is a lightweight Python web framework
- It handles HTTP requests and responses
- It serves the frontend and provides API endpoints
"""

from flask import Flask, render_template, request, jsonify
from llm import friday
from vision import vision
import base64
import traceback

# Initialize Flask app
app = Flask(__name__)

# Configure Flask
app.config['SECRET_KEY'] = 'friday-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload


@app.route('/')
def index():
    """
    Serve the main frontend page.
    
    Returns:
        Rendered HTML template
    """
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API endpoint for text chat.
    
    Expects JSON:
        {"message": "user message"}
    
    Returns:
        JSON response with FRIDAY's reply
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get response from FRIDAY
        response = friday.ask_friday(user_message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint for screen analysis.
    
    Expects JSON:
        {"image": "base64_image_data", "question": "user question"}
    
    Returns:
        JSON response with FRIDAY's analysis
    """
    try:
        data = request.get_json()
        image_base64 = data.get('image', '').strip()
        user_question = data.get('question', '').strip()
        
        if not image_base64:
            return jsonify({'error': 'Image data cannot be empty'}), 400
        
        if not user_question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get analysis from FRIDAY
        analysis = friday.analyze_screen(image_base64, user_question)
        
        return jsonify({'analysis': analysis})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/capture', methods=['POST'])
def capture():
    """
    API endpoint for screen capture.
    
    Returns:
        JSON response with base64 encoded screenshot
    """
    try:
        # Capture screen
        image_path = vision.capture_screen()
        
        # Encode to base64
        image_base64 = vision.encode_image_base64(image_path)
        
        return jsonify({'image': image_base64})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/region', methods=['POST'])
def capture_region():
    """
    API endpoint for region capture.
    
    Expects JSON:
        {"x1": 100, "y1": 100, "x2": 800, "y2": 600}
    
    Returns:
        JSON response with base64 encoded region screenshot
    """
    try:
        data = request.get_json()
        x1 = int(data.get('x1', 0))
        y1 = int(data.get('y1', 0))
        x2 = int(data.get('x2', 0))
        y2 = int(data.get('y2', 0))
        
        # Capture region
        image_path = vision.capture_region(x1, y1, x2, y2)
        
        # Encode to base64
        image_base64 = vision.encode_image_base64(image_path)
        
        return jsonify({'image': image_base64})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    """
    Run the Flask development server.
    
    In production, use a proper WSGI server like Gunicorn or uWSGI.
    """
    app.run(debug=True, host='0.0.0.0', port=5000)
