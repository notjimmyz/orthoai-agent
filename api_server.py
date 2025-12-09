"""Backend API server for React frontend to communicate with agents."""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from src.my_util import my_a2a

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend


async def check_agent_ready(url):
    """Check if an agent is ready"""
    try:
        ready = await my_a2a.wait_agent_ready(url, timeout=2)
        return ready
    except Exception:
        return False


async def send_message_to_agent(url, message):
    """Send a message to an agent and get response"""
    try:
        response = await my_a2a.send_message(url, message)
        
        # Extract text from response
        from a2a.utils import get_text_parts
        text_parts = get_text_parts(response.root.result.parts)
        
        if text_parts:
            return text_parts[0]
        else:
            return str(response.root.result)
    except Exception as e:
        raise Exception(f"Failed to send message: {str(e)}")


def run_async(coro):
    """Helper to run async functions in Flask"""
    # Create a new event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        return new_loop.run_until_complete(coro)
    finally:
        new_loop.close()


@app.route('/api/check-agent', methods=['GET'])
def check_agent():
    """Check if an agent is ready"""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter required'}), 400
    
    try:
        ready = run_async(check_agent_ready(url))
        return jsonify({'ready': ready})
    except Exception as e:
        return jsonify({'error': str(e), 'ready': False}), 500


@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Send a message to an agent"""
    data = request.get_json()
    url = data.get('url')
    message = data.get('message')
    
    if not url or not message:
        return jsonify({'error': 'URL and message required'}), 400
    
    try:
        response_text = run_async(send_message_to_agent(url, message))
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = 5001  # Use 5001 to avoid conflict with macOS AirPlay on 5000
    print(f"Starting API server on http://localhost:{port}")
    print("Make sure your agents are running on ports 9001 (green) and 9002 (white)")
    app.run(host='0.0.0.0', port=port, debug=True)

