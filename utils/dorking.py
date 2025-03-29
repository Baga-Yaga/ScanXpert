import os


from groq import Groq
import re
client = Groq(
    api_key="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",
)

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



def generate_ai_powered_dork(options):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "I'll give you a prompt to generate dork and you give me 3-4 different dork query with little variatians which will reflect best way to my prompt...give all dorks with best queires, advanced level, and maybe add some of your own best additional thing in it and give response in one line seperated by $ symbol. One more important thing, any prompt from user/me which is not related to dork, or you wont understand or is like some scame query, just ignore  and response as 'invalid query'",
            },
            {
                "role": "user",
                "content": options.get("prompt", "")
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    # print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content 
