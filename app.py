import os
import socket
from flask import Flask, jsonify, request, render_template, Response
import subprocess, json
from backend import *
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='/', static_url_path='/')
CORS(app)

@app.route('/')
def greet():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -------------------------- Subdomain Enumeration -----------------------

@app.route('/subdomain_enum')
def subdomain_enum():
    return render_template('subdomain_enum.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    domain = request.form.get('domain')
    if not domain:
        return "No domain provided", 400

    def run_scan(domain):
        process = subprocess.Popen(
            ['python3', 'backend/subdomain_enum.py', domain, '--enum'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in iter(process.stdout.readline, ''):
            yield f"{line.strip()} \n"
        process.stdout.close()
        yield "[ SCAN COMPLETED ]\n\n"
    
    return Response(run_scan(domain), mimetype='text/event-stream')

@app.route('/summary')
def summary():
    domain = request.args.get('domain')
    if not domain:
        return "No domain provided", 400
    try:
        process = subprocess.Popen(
            ['python3', 'backend/subdomain_enum.py', domain, '--summary'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )  
        output, _ = process.communicate()
        return output
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output"}, 500

@app.route('/detailed_results')
def get_detailed_results():
    domain = request.args.get('domain')
    file_path = f'{domain}_report/live_domain_detail.json'
    if not domain:
        return "No domain provided", 400
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                json_content = f.read()
            json_objects = [json.loads(line) for line in json_content.strip().split('\n') if line]
            return jsonify(json_objects)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON output"}, 500
    else:
        return {"error": "File not found"}, 404

# -------------------------- Google Dorking -----------------------

@app.route('/dorking')
def dorking():
    return render_template('dorking.html')

# -------------------------- Wayback URL Fetching -----------------------

@app.route('/Wayback')
def Wayback():
    return render_template('wayback.html')

@app.route('/fetch_wayback', methods=['POST'])
def fetch_wayback():
    domain = request.form.get('domain')
    if not domain:
        return jsonify({"error": "No domain provided"}), 400

    try:
        result = subprocess.run(
            ["python3", "backend/wayback.py", domain],
            capture_output=True, text=True, check=True
        )
        return jsonify({'output': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr}), 500

# -------------------------- Network Scanning -----------------------

@app.route('/network_scan')
def network_scan():
    return render_template('network_scan.html')

# -------------------------- Dynamic Port Selection -----------------------

def find_available_port(start_port=5000):
    """ Finds an available port starting from `start_port` """
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1

if __name__ == '__main__':
    port = find_available_port(5000)
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
