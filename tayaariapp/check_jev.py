import subprocess
import sys

# Try running npx with cmd
result = subprocess.run(['npx', '-y', 'jev-judge-mcp', '--help'], capture_output=True, text=True, timeout=60, shell=True)
print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)