import subprocess,argparse
import os,json

def subdomain_enum(domain):
    output_dir = f"{domain}_report"
    os.makedirs(output_dir,exist_ok=True)
    output_file = os.path.join(output_dir,"tmpdomain")
    print("Fetching subdomains using subfinder...")
    subprocess.run(
        f"subfinder -d {domain} -recursive -all -silent > {output_file}",
        shell=True,
        check=True
    )
    print("Fetching subdomains using assetfinder...")
    subprocess.run(
        f"assetfinder --subs-only {domain} >> {output_file}",
        shell=True,
        check=True
    )
    # print("Fetching subdomains using findomain...")
    # subprocess.run(
    #     f"findomain -t {domain} >> {output_file}",
    #     shell=True,
    #     check=True
    # )
    refined = os.path.join(output_dir,"subdomains")
    try:
        subprocess.run(
            f"cat {output_file} | grep -Eo '\\b([a-zA-Z0-9-]+\\.)+[a-zA-Z]{{2,}}\\b' > {refined}", 
            shell=True, check=True
        )
        print("\n[+] Subdomains extracted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during grep command: {e}")
     
    print("\n[.] Extracting active subdomains...")
    active_file = f"{output_dir}/activesubs"
    subprocess.run(
        f"cat {output_file} | httpx -silent > {active_file}",
        shell=True,
        check=True
    )
    
    jsonfile = f"{output_dir}/live_domain_detail.json"
    subprocess.run(
        "cat "+ active_file + "| httpx -silent -j | jq -c '{subdomain:.input,ip:.host,port:.port,status_code:.status_code,tech:.tech}'  > " + jsonfile ,
        shell=True,
        check=True
    )
    with open(active_file, 'r') as r:
        result = r.read()
        print(result)
    print('[✓] Extracted Successfully')

def scan_summary(domain):
    output_dir = f"{domain}_report"
    output_file = os.path.join(output_dir, "subdomains")
    active_file = os.path.join(output_dir, "activesubs")
    jsonfile = os.path.join(output_dir, "live_domain_detail.json")
    
    summary = {'total':0,'live':0,'2xx':0,'3xx':0,'4xx':0,'5xx':0}
    sc2, sc3, sc4, sc5 = 0, 0, 0, 0
    with open(output_file, 'r') as f1:
        total = sum(1 for line in f1 if line.strip())
        summary['total'] = total
    with open(active_file, 'r') as f2:
        live = sum(1 for line in f2 if line.strip())
        summary['live'] = live
    with open(jsonfile, 'r') as f3:
        for line in f3:
            if line.strip(): 
                try:
                    data = json.loads(line) 
                    if 'status_code' in data:
                        status_code = int(data['status_code'])
                        if 200 <= status_code < 300:
                            sc2 += 1
                            summary['2xx'] = sc2
                        elif 300 <= status_code < 400:
                            sc3 += 1
                            summary['3xx'] = sc3
                        elif 400 <= status_code < 500:
                            sc4 += 1
                            summary['4xx'] = sc4
                        elif 500 <= status_code < 600:
                            sc5 += 1
                            summary['5xx'] = sc5
                    else:
                        print(f"Skipping entry: 'status_code' not found in {data}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    continue
    # print("\n[+] Scan Summary:")
    print(json.dumps(summary, indent=4))

def table_content(domain):
    output_dir = f"{domain}_report"
    jsonfile = os.path.join(output_dir, "live_domain_detail.json")
    with open(jsonfile, 'r') as f3:
        for line in f3:
            if line.strip(): 
                try:
                    data = json.loads(line) 
                    print(data)
                except json.JSONDecodeError as e:
                    print(e)
        
        # return f'\n[+]Out of {sub} subdomains, their are {sub2} active subdomains'
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain Enumeration Tool")
    parser.add_argument("domain", help="Target domain for subdomain enumeration")
    parser.add_argument("--enum", action="store_true", help="Run subdomain enumeration")
    parser.add_argument("--summary", action="store_true", help="Generate scan summary")
    parser.add_argument("--table", action="store_true", help="Generate table content")
    args = parser.parse_args()

    if args.enum:
        subdomain_enum(args.domain)
    if args.summary:
        scan_summary(args.domain)
    if args.table:
        table_content(args.domain)