import re
import subprocess

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
    # Looking for text between quotes or until the next space
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

    # 1. Port/Protocol Check (Error #1 and #4)
    if parts["proxy_url"]:
        if ":65534" in parts["proxy_url"] and "https://" in parts["proxy_url"]:
            errors.append("Port 65534 is for HTTP. Use 'http://' protocol.")
        elif ":65535" in parts["proxy_url"] and "http://" in parts["proxy_url"]:
            errors.append("Port 65535 is for HTTPS. Use 'https://' protocol.")
        
        # Check for legacy host (Error #2)
        if "isp.joinmassive.com" in parts["proxy_url"]:
            warnings.append("Host 'isp.joinmassive.com' might be legacy. Use 'network.joinmassive.com'.")

    # 2. Authentication and Geotargeting Check (Error #3 and #4)
    if parts["auth_block"]:
        if ":" in parts["auth_block"]:
            username, password = parts["auth_block"].split(":", 1)
            
            # Check parameter placement
            if any(key in password for key in ["-country-", "-city-", "-zipcode-"]):
                errors.append("Geotargeting parameters must be in the Username section (before the colon).")
            
            # Check ISO code
            if "-country-UK" in username:
                warnings.append("'UK' is not a standard ISO code. Use 'GB' for United Kingdom.")
        else:
            errors.append("Invalid credentials format. Use 'username:password'.")

    # Final report generation
    if not errors and not warnings:
        return "Success: Request looks valid according to Massive documentation."
    
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
        # split the string into a list of arguments correctly
        # this handles quotes and spaces much better than shell=True
        args = shlex.split(curl_command)
        
        # We replace 'curl' with 'curl.exe' for Windows stability
        if args[0] == 'curl':
            args[0] = 'curl.exe'
            
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