import os
import re
import subprocess
from typing import List, Optional

def clean_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def parse_url_line(line: str) -> Optional[List[str]]:
    try:
        line = clean_ansi(line).strip()
        
        if not line:
            return None
            
        parts = line.split(' [', 1)
        url_part = parts[0].strip()
      
        if len(parts) == 1:
            return [url_part, '-', '-']
            
        rest_part = parts[1]
        
        status_match = re.search(r'^(\d+)\]', rest_part)
        status_code = status_match.group(1) if status_match else '-'
       
        title_match = re.search(r'\] \[([^\]]*)', rest_part)
        title = title_match.group(1).strip() if title_match else '-'
        
        return [url_part, status_code, title]
        
    except Exception as e:
        print(f"Error parsing line: {line} - {str(e)}")
        return None

def result_parser(output_file: str) -> List[List[str]]:
    results = []
    if not os.path.exists(output_file):
        return results
        
    try:
        with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parsed = parse_url_line(line)
                if parsed:
                    results.append(parsed)
    except Exception as e:
        print(f"Error reading file {output_file}: {str(e)}")
        
    return results

def sanitize_domain(domain: str) -> str:
    if domain.startswith("https://"):
        return domain[8:]
    elif domain.startswith("http://"):
        return domain[7:]
    return domain

def get_output_paths(domain: str) -> tuple:
    outdomain = sanitize_domain(domain)
    output_dir = os.path.join("backend/reports", outdomain)
    output_file = os.path.join(output_dir, "waybackurls.txt")
    return output_dir, output_file

def getallurls(domain: str) -> List[List[str]]:
    """Main function to get all URLs for a domain"""
    output_dir, output_file = get_output_paths(domain)
    os.makedirs(output_dir, exist_ok=True)
    print(os.getcwd())
    try:
        subprocess.run(
            ["./backend/waybackscanner.sh", domain],
            check=True,
            timeout=600 
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during subprocess: {e}")
    except subprocess.TimeoutExpired:
        print("Subprocess timed out.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return result_parser(output_file)

def filter_urls(mode: str, domain: str) -> List[List[str]]:
    output_dir, _ = get_output_paths(domain)
    
    if mode == "xss":
        return result_parser(os.path.join(output_dir, "xss.txt"))
    elif mode == "sqli":
        return result_parser(os.path.join(output_dir, "sqli.txt"))
    elif mode == "lfi":
        return result_parser(os.path.join(output_dir, "lfi.txt"))
    elif mode == "js":
        return result_parser(os.path.join(output_dir, "js.txt"))
    elif mode == "ssrf":
        return result_parser(os.path.join(output_dir, "ssrf.txt"))
    elif mode == "all":
        return result_parser(os.path.join(output_dir, "waybackurls.txt"))
    else:
        return []
