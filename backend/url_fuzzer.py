import subprocess
import os
import threading

progress_tracker = {}

def run_url_fuzzer(domain, scan_type):
    # domain = re.sub(r'[^a-zA-Z0-9_.-]', '', domain)
    if domain.startswith("https://"):
        outdomain = domain[8:] 
        output_dir = f"reports/{outdomain}"
    elif domain.startswith("http://"):
        outdomain = domain[7:]
        output_dir = f"reports/{outdomain}"
    else:
        output_dir = f"reports/{domain}"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "urlfuzzer.csv")

    cmd = f"dirsearch -u {domain} -i 200,403,401 --max-rate 80 --format=csv --output={output_file}"
    if scan_type == 2:
        cmd += " -w ../wordlist/raft-large-directories-lowercase.txt"
    elif scan_type == 3:
        cmd += " -w ../wordlist/httparchive_directories_1m_2024_04_28.txt"

    def scan():
        progress_tracker[domain] = 0
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            for line in proc.stdout:
                if '%' in line:
                    parts = line.strip().split()
                    for part in parts:
                        if '%' in part:
                            try:
                                percent = int(part.replace('%', ''))
                                progress_tracker[domain] = percent
                            except:
                                pass
        progress_tracker[domain] = 100

    threading.Thread(target=scan).start()
    return output_file

def get_progress(domain):
    return progress_tracker.get(domain, 0)

def parse_csv_results(domain):
    if domain.startswith("https://"): 
        outdomain = domain[8:] 
        output_file = f"reports/{outdomain}/urlfuzzer.csv"
    elif domain.startswith("http://"):
        outdomain = domain[7:]
        output_file = f"reports/{outdomain}/urlfuzzer.csv"
    else:        
        output_file = f"reports/{domain}/urlfuzzer.csv"
    results = []
    if os.path.exists(output_file):
        with open(output_file, 'r') as file:
            lines = file.readlines()[1:]  
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    url, code, size, _ = parts[:4]
                    status = 'OK' if code == '200' else ('Forbidden' if code == '403' else 'Redirect' if code == '302' else 'Other')
                    results.append([url, code, status, size])
    return results
