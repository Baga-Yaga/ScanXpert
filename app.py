import os
from flask import Flask, jsonify, request, render_template, Response
import subprocess, json, re
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

def validate_domain(domain):
    pattern = r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,6}$"
    return bool(re.match(pattern, domain))

def generate_dork_query(options):
    query_parts = []
    target_url = options.get("targetUrl", "").strip()
    if not validate_domain(target_url):
        return "Invalid target domain"
    query_parts.append(f"site:{target_url}")
    
    dork_type_map = {
        "adminUrl": "inurl:admin",
        "inTitle": "intitle:index of",
        "sensitiveFile": "ext:log | ext:sql | ext:env",
        "cachePage": "cache:"
    }
    dork_type = dork_type_map.get(options.get("dorkType", ""), "")
    if dork_type:
        query_parts.append(dork_type)
    if options.get("dorkType") == "fileType":
        file_extensions = ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "log", "sql", "env"]
        query_parts.append(" OR ".join([f"filetype:{ext}" for ext in file_extensions]))
    
    if options.get("sqlDatabase"):
        query_parts.append("inurl:php?id=")
    if options.get("openDirectory"):
        query_parts.append("intitle:\"index of\"")
    if options.get("sensitiveFiles"):
        query_parts.append("ext:log | ext:sql | ext:env")
    if options.get("cameraFeed"):
        query_parts.append("inurl:/view/view.shtml")
    if options.get("subdomainEnumeration") and target_url:
        query_parts.remove(f"site:{target_url}")
        query_parts.append(f"site:*.{target_url}")
    if options.get("credentialLeak"):
        query_parts.append("intitle:\"password\" OR intext:\"password\"")
    
    exclude_sites = options.get("excludeSite", [])
    for site in exclude_sites:
        if validate_domain(site):
            query_parts.append(f"-site:{site}")
    
    time_range = options.get("timeRange", 0)
    if isinstance(time_range, int) and time_range > 0:
        query_parts.append(f"after:{time_range}")
    
    if options.get("findLogins"):
        query_parts.append("inurl:login")
    if options.get("filterDuplicates"):
        query_parts.append("&filter=0")
    
    additional_params = options.get("additionalParameters", "").strip()
    if additional_params:
        query_parts.append(additional_params)
    
    return " ".join(query_parts)

@app.route('/generate_query', methods=['POST'])
def generate_query():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input format"}), 400
    query = generate_dork_query(data)
    return jsonify({"query": query})

# -------------------------- Network Scanning -----------------------

@app.route('/network_scan')
def network_scan():
    return render_template('network_scan.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
