from flask import Flask, request, render_template,Response,stream_with_context,jsonify
import subprocess
from flask_cors import CORS
import re
app = Flask(__name__,template_folder='templates',static_folder='/',static_url_path='/')
CORS(app)

@app.route('/')
def greet():
	return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --------------------------This code block belongs to subdomain enumeration -----------------------

@app.route('/subdomain_enum')
def subdomain_enum():
    return render_template('subdomain_enum.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    domain = request.form.get('domain')
    if not domain:
        return "No domain provided", 400

    def run_scan(domain):
        """Generator function to yield live output of the subfinder command."""
        process = subprocess.Popen(
            ['subfinder', '-d', domain, '-silent'],  # Run subfinder command
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            yield  f"{line.strip()} \n"  

        process.stdout.close()
        process.wait()
        yield "[ SCAN COMPLETED ]\n\n"

    return Response(run_scan(domain), mimetype='text/event-stream')



# --------------------------This code block belongs to dorking -----------------------

def validate_domain(domain):
    pattern = r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,6}$"
    print(domain, bool(re.match(pattern, domain))   )
    return bool(re.match(pattern, domain))

def generate_dork_query(options):
    print(options)
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

    
    # Quick tool options
    if options.get("sqlDatabase"):
        query_parts.append("inurl:php?id=")
    if options.get("openDerictory"):
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
    
    # Exclude specific sites
    exclude_sites = options.get("excludeSite", [])
    for site in exclude_sites:
        if validate_domain(site):
            query_parts.append(f"-site:{site}")
    
    # Time range filtering (assuming input is in days)
    time_range = options.get("timeRange", 0)
    if isinstance(time_range, int) and time_range > 0:
        query_parts.append(f"after:{time_range}")
    
    # Login page search
    if options.get("findLogins"):
        query_parts.append("inurl:login")
    
    # Filter out duplicates (forcing unique results)
    if options.get("filterDuplicates"):
        query_parts.append("&filter=0")
    
    # Additional parameters
    additional_params = options.get("additioalParameters", "").strip()
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

# --------------------------------------------------------------------------------------------------

#this code belongs to google dorking

@app.route('/dorking')
def dorking():
    return render_template('dorking.html')














#----------------------------------------------------------------------------------------------------

@app.route('/network_scan')
def network_scan():
    return render_template('network_scan.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)

