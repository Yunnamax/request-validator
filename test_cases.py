from validator import validate_request

examples = [
    "curl --proxy https://network.joinmassive.com:65534 -U '{PROXY_USERNAME}:{API_KEY}' ip-api.com",
    "curl --proxy http://network.joinmassive.com:65534 -U 'user:key' ip-api.com"
]

for cmd in examples:
    result = validate_request(cmd)
    print(f"Testing: {cmd}\nResult: {result if result else '✅ Valid'}\n")