import re
import subprocess
import platform

def parse_curl(curl_string):
    """Parses curl into parts: proxy, authentication, and target URL."""
    """Example input:"""
    """curl --proxy https://network.joinmassive.com:65535 --proxy-user 'PROXY_USERNAME:API_KEY' https://cloudflare.com/cdn-cgi/trace"""
    parts = {
        "proxy_url": None,
        "auth_block": None,
        "target_url": None
    }
    
    # Extract proxy address (--proxy or -x)
    proxy_match = re.search(r'(?:--proxy|-x)\s+([\S]+)', curl_string)
    if proxy_match:
        parts["proxy_url"] = proxy_match.group(1)
        
    # Extract authentication (-U or --proxy-user)
    auth_match = re.search(r'(?:-U|--proxy-user)\s+[\'"]?([^\s\'"]+)[\'"]?', curl_string)
    if auth_match:
        parts["auth_block"] = auth_match.group(1)
    
    # Extract target URL 
    target_match = re.search(r'\s+([^\s\-][\S]+)$', curl_string.strip())
    if target_match:
        parts["target_url"] = target_match.group(1)
        
    return parts

def validate_request(curl_input):
    if not curl_input.strip():
        return "Error: Empty input. Please provide a curl command."
    
    parts = parse_curl(curl_input)
    errors = []
    warnings = []

# 1. Port/Protocol/Host Check (Error #1 and #4)
    if parts["proxy_url"]:
        proxy_url = parts["proxy_url"].lower()
        
        # HTTPS Check
        if ":65535" in proxy_url and not proxy_url.startswith("https://"):
            errors.append("Port 65535 is for HTTPS. Your proxy URL should start with 'https://'.")
        
        # HTTP Check
        elif ":65534" in proxy_url and not proxy_url.startswith("http://"):
            # Note: curl might default to http, but explicit is better
            errors.append("Port 65534 is for HTTP. Your proxy URL should start with 'http://'.")
            
        # SOCKS5 Check (Adding this from documentation)
        elif ":65533" in proxy_url and not proxy_url.startswith("socks5://"):
            errors.append("Port 65533 is for SOCKS5. Your proxy URL should start with 'socks5://'.")

        # Reverse check: if protocol is used with wrong port
        if proxy_url.startswith("https://") and ":65535" not in proxy_url:
            warnings.append("You are using HTTPS protocol but not on the standard port 65535.")
        
    # 2. Check for wrong host (Error #2)
        if "isp.joinmassive.com" in parts["proxy_url"]:
            warnings.append("Host 'isp.joinmassive.com' is wrong host. Use 'network.joinmassive.com'.")

    # 3. Authentication and Geotargeting Check (Error #3 and #4)
    if parts["auth_block"]:
            if ":" in parts["auth_block"]:
                username, password = parts["auth_block"].split(":", 1)
                username_lower = username.lower()
                
                # Ensure parameters are not placed in the password field
                geo_keys = ["-country-", "-city-", "-zipcode-", "-subdivision-"]
                if any(key in password for key in geo_keys):
                    errors.append("Geotargeting parameters must be in the Username section (before the colon).")
                
                # Check for mandatory country key when other geo-parameters are present
                has_country = "-country-" in username_lower
                has_other_geo = any(key in username_lower for key in ["-city-", "-zipcode-", "-subdivision-"])
                if has_other_geo and not has_country:
                    errors.append("HTTP 400 Risk: 'country' parameter is mandatory when using city, zipcode, or subdivision.")

                # Identify if city will be ignored due to zipcode priority
                if "-zipcode-" in username_lower and "-city-" in username_lower:
                    warnings.append("Optimization: 'city' will be ignored by the server because 'zipcode' is specified.")
                
                # Verify ISO country code compliance
                if "-country-uk" in username_lower:
                    warnings.append("'UK' is not a standard ISO code. Use 'GB' for United Kingdom.")
            else:
                errors.append("Invalid credentials format. Use 'username:password'.")

    # Final report generation
    if not errors and not warnings:
        return "Success: Request looks valid. No issues detected."
    
    report = ["\n--- Analysis Report ---"]
    for err in errors:
        report.append(f"ERROR: {err}")
    for warn in warnings:
        report.append(f"WARNING: {warn}")
    
    return "\n".join(report)

def execute_curl(curl_command):
    """Executes the curl command safely using shlex to split arguments."""
    import shlex
        
    try:
        args = shlex.split(curl_command)
            
        # Check the Operating System
        if platform.system() == "Windows":
            if args[0] == 'curl':
                args[0] = 'curl.exe'
            else:
                # On Linux/macOS, we ensure it's just 'curl'
                if args[0] == 'curl.exe':
                    args[0] = 'curl'
            
        process = subprocess.run(args, capture_output=True, text=True)
        
        if process.returncode == 0:
            return f"Response from server:\n{process.stdout}"
        else:
            # If we get 407 here, we know it's a data issue, not a shell issue
            return f"Execution Error (Code {process.returncode}):\n{process.stderr}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def main():
    print("--- Massive Request Validator & Executor ---")
    print("Enter 'exit' to quit.")
    
    while True:
        user_input = input("\nPlease enter your curl command: ")
        if user_input.lower() == 'exit':
            break
            
        validation_result = validate_request(user_input)
        print(validation_result)
        
        # If validation passed, ask if the user wants to run it
        if "Success" in validation_result:
            confirm = input("Validation passed. Execute this request? (y/n): ")
            if confirm.lower() == 'y':
                print("Executing...")
                print(execute_curl(user_input))

if __name__ == "__main__":
    main()