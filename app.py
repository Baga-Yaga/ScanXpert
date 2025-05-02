import datetime
import os
import socket
import threading
from flask import Flask, jsonify, request, render_template, Response
import subprocess, json
from utils.dorking import generate_dork_query, generate_ai_powered_dork # type: ignore
from backend import url_fuzzer
from backend import waybackurl
from backend import *
from flask_cors import CORS # type: ignore

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

@app.route('/generate_query', methods=['POST'])
def generate_query():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input format"}), 400
    
    query = generate_dork_query(data)
    return jsonify({"query": query})


@app.route('/generate_ai_query', methods=['POST'])
def generate_ai_query():
    data = request.get_json()
    # if not isinstance(data, dict):
    #     return jsonify({"error": "Invalid input format"}), 400
    if(len(data.get("prompt",""))==0):
        return jsonify({"error": "Invalid input format"}), 400
    
    
    query = generate_ai_powered_dork(data)
    print(query.split(" $ "))
    return jsonify({"query": query})

# -------------------------- Wayback URL Fetching -----------------------
@app.route('/wayback')
def wayback_page():
    return render_template('wayback.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    domain = data.get('domain')
    if not domain:
        return jsonify({"error": "No domain provided"}), 400
    
    results = waybackurl.getallurls(domain)
    return jsonify(results)

@app.route('/filter', methods=['POST'])
def filter_mode():
    data = request.get_json()
    domain = data.get('domain')
    mode = data.get('mode')
    
    if not domain or not mode:
        return jsonify({"error": "Missing domain or mode"}), 400

    results = waybackurl.filter_urls(mode, domain)
    return jsonify(results)
    
# -------------------------- URL Fuzzer -----------------------
@app.route('/url_fuzzer')
def url_fuzzer_page():
    return render_template('url_fuzzer.html')

@app.route('/start_url_fuzzer', methods=['POST'])
def start_url_fuzzer():
    data = request.get_json()
    domain = data['domain']
    scan_type = int(data['type'])

    url_fuzzer.run_url_fuzzer(domain, scan_type)
    return jsonify({'status': 'started'})

@app.route('/fuzz_progress')
def fuzz_progress():
    domain = request.args.get('domain')
    progress = url_fuzzer.get_progress(domain)
    return jsonify({'progress': progress})

@app.route('/fuzz_result')
def fuzz_result():
    domain = request.args.get('domain')
    results = url_fuzzer.parse_csv_results(domain)
    return jsonify({'results': results})

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
