Request Validator & Executor
A Python-based CLI tool designed to assist in validating and executing curl commands. It ensures that requests adhere to official documentation, preventing common connectivity and authentication errors.

🚀 Features
Syntax Validation: Parses curl commands to extract proxy settings, credentials, and target URLs.

Documentation Compliance:

Port/Protocol Check: Ensures HTTPS (65535), HTTP (65534), and SOCKS5 (65533) are used with correct protocols.

Geotargeting Logic: Verifies that parameters like -country-, -city-, and -zipcode- are placed correctly in the username section to avoid 407 Authentication Errors.

Mandatory Fields: Checks for the presence of the -country- key when other geo-parameters are used (preventing HTTP 400).

Wrong Host Detection: Warns if the outdated isp.joinmassive.com host is used.

Cross-Platform Support: Automatically handles curl vs curl.exe depending on the operating system (Windows, macOS, Linux).

Safe Execution: Uses shlex for secure command execution and displays server responses or detailed error logs.

🛠 Installation & Usage
Clone the repository:

Bash
git clone <your-repo-link>
Run the validator:

Bash
python validator.py
Run automated tests:
To verify the tool against standard error cases, run:

Bash
python test_cases.py