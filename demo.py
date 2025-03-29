import json

with open('actcorp.in_report/live_domain_detail.json','r')as f:
    jsonl_content = f.read()
# Split lines and parse each JSON object
json_objects = [json.loads(line) for line in jsonl_content.strip().split('\n') if line]

# Convert to JSON array
json_array = json.dumps(json_objects, indent=2)
print(json_array)