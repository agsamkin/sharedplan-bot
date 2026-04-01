import subprocess
import sys
import re

result = subprocess.run(
    ["pytest", "--cov=app", "--cov=mini_app", "--cov-report=term"],
    capture_output=True, text=True
)

for line in result.stdout.splitlines():
    if "TOTAL" in line:
        match = re.search(r'(\d+)%', line)
        if match:
            coverage = int(match.group(1))
            print(coverage)
            sys.exit(0)

print("0")
sys.exit(1)