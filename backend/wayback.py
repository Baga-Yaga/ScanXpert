import subprocess
import os

def wayback_enum(domain):
    output_dir = f"{domain}_report"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "wayback_urls")

    print("Fetching archived URLs using waybackurls...")
    subprocess.run(
        f"waybackurls {domain} | tee {output_file}",
        shell=True,
        check=True
    )

    print("\n[+] Extracting unique URLs...")
    refined = os.path.join(output_dir, "wayback_unique")
    subprocess.run(
        f"cat {output_file} | sort -u > {refined}", 
        shell=True, check=True
    )

    with open(refined, 'r') as r:
        result = r.read()
        print(result)
    
    print('[✓] Wayback URLs Extracted Successfully')

# Paste this at the end of the file
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Wayback URL Extractor")
    parser.add_argument("domain", help="Target domain for Wayback enumeration")
    args = parser.parse_args()

    wayback_enum(args.domain)
