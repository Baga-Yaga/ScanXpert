import os
from flask import Flask, jsonify, request, render_template,Response,stream_with_context
import subprocess,json
from backend import *
app = Flask(__name__,template_folder='templates',static_folder='/',static_url_path='/')

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
            ['python3','backend/subdomain_enum.py', domain, '--enum'],  # Run subfinder command
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            yield  f"{line.strip()} \n"  

        process.stdout.close()
        # process.wait()
        yield "[ SCAN COMPLETED ]\n\n"
    return Response(run_scan(domain), mimetype='text/event-stream')

@app.route('/summary')
def summary():
    domain = request.args.get('domain')
    if not domain:
        return "No domain provided", 400
    try:
        process = subprocess.Popen(
            ['python3','backend/subdomain_enum.py', domain, '--summary'],  # Run subfinder command
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )  
        output, _ = process.communicate()   
        return  output
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output"}, 500
    
@app.route('/detailed_results')
def getable():
    domain = request.args.get('domain')
    file_path = f'{domain}_report/live_domain_detail.json'
    if not domain:
        return "No domain provided", 400
    if os.path.exists(file_path):
        try:
            with open(file_path,'r')as f:
                json_content = f.read() 
            json_objects = [json.loads(line) for line in json_content.strip().split('\n') if line]
            json_array = json.dumps(json_objects, indent=2)
            return jsonify(json_array)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON output"}, 500
    else:
        return {"error":"File not found"},404
    

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

