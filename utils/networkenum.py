import os
import re
import json
from groq import Groq
client = Groq(
    api_key="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",
)
import nmap
def start_network_scan(data):
    if 'target' not in data or not data['target'].strip():
        raise ValueError("Target IP or range is required.")

    ip_regex = r"^(?:(?:\d{1,3}\.){3}\d{1,3})(?:/\d{1,2})?$"
    if not re.match(ip_regex, data['target'].strip()):
        raise ValueError("Invalid IP address or CIDR range.")

    allowed_profiles = {'ping', 'quick', 'intense', 'stealth', 'custom'}
    profile = data.get('profile', 'quick')
    if profile not in allowed_profiles:
        raise ValueError(f"Invalid scan profile: {profile}")

    custom_ports = data.get('customPorts', '').strip()
    if custom_ports:
        port_pattern = r'^(\d{1,5}(-\d{1,5})?)(,(\d{1,5}(-\d{1,5})?))*$'
        if not re.match(port_pattern, custom_ports):
            raise ValueError("Invalid custom ports format.")

    checkbox_fields = ['tcpScan', 'udpScan', 'osDetection', 'versionDetection', 'hostDiscovery', 'scriptScan']
    for key in checkbox_fields:
        if key in data and not isinstance(data[key], bool):
            raise ValueError(f"{key} must be a boolean.")

    custom_flags = data.get('customFlags', '')
    if custom_flags and any(char in custom_flags for char in [';', '&', '|']):
        raise ValueError("Custom flags contain potentially dangerous characters.")

    # ------------------- Build Nmap Command -------------------
    scanner = nmap.PortScanner()
    args = ''

    # Preset scan profiles
    if profile == 'ping':
        args = '-sn'
    else:
        if profile == 'quick':
            args = '-T4 -F'
        elif profile == 'intense':
            args = '-T4 -A -v'
        elif profile == 'stealth':
            args = '-sS -T3'
        elif profile == 'custom':
            args = '' 

    if data.get('tcpScan'):
        args += ' -sS'
    if data.get('udpScan'):
        args += ' -sU'
    if data.get('osDetection'):
        args += ' -O'
    if data.get('versionDetection'):
        args += ' -sV'
    if data.get('hostDiscovery'):
        args = '-sn'  # overrides everything
    if data.get('scriptScan'):
        args += ' -sC'
    if custom_ports:
        args += f' -p {custom_ports}'
    if custom_flags:
        args += f' {custom_flags}'

    target = data['target'].strip()

    print(f"Running scan on {target} with args: {args}")
    try:
        scanner.scan(hosts=target, arguments=args)
        result = scanner.all_hosts()

        output = {}
        for host in result:
            output[host] = scanner[host]

        return format_results_ai({
            'status': 'success',
            'scan_args': args.strip(),
            'result': output
        })

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
    
def format_results_ai(data):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
You are a Markdown formatter. Only format the following JSON result into clean, minimal, and readable Markdown.
Do not explain anything. Do not include any theory or assumptions and also handle errors formatting. 

Input JSON:
{json.dumps(data, indent=2)}

Output:
"""
,
            },
        ],
        model="llama-3.3-70b-versatile",
    )
    print(data)
    # print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content 