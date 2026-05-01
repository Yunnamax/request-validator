from validator import validate_request

# Список усіх кейсів від Джоша
test_queries = [
    # Case 1: Wrong protocol for port 65534 (HTTPS instead of HTTP)
    "curl --proxy https://network.joinmassive.com:65534 -U '{PROXY_USERNAME}:{API_KEY}' ip-api.com",
    
    # Case 2: Legacy host (isp) and non-standard port (4000)
    "curl --proxy http://isp.joinmassive.com:4000 -U '{PROXY_USERNAME}:{API_KEY}' https://cloudflare.com/cdn-cgi/trace",
    
    # Case 3: Geotargeting in the Password section (after the colon)
    "curl --proxy https://network.joinmassive.com:65535 -U '{PROXY_USERNAME}:{API_KEY}-country-US' https://cloudflare.com/cdn-cgi/trace",
    
    # Case 4: Wrong ISO code (UK instead of GB) and port mismatch (65534 with https?)
    "curl --proxy https://network.joinmassive.com:65534 -U '{PROXY_USERNAME}-country-UK-city-London:{API_KEY}' https://cloudflare.com/cdn-cgi/trace"
]

def run_tests():
    print("=== RUNNING ALL TEST CASES FROM JOSH ===\n")
    
    for i, cmd in enumerate(test_queries, 1):
        print(f"TEST CASE #{i}")
        print(f"COMMAND: {cmd}")
        
        # Викликаємо твою функцію валідації
        report = validate_request(cmd)
        print(report)
        print("-" * 50)

if __name__ == "__main__":
    run_tests()