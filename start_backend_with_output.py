import subprocess
import sys

# Start the backend and capture output
process = subprocess.Popen(
    [sys.executable, "-m", "app.main_enhanced"],
    cwd="/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print("Starting backend server...")
print("-" * 50)

# Read output line by line
for line in process.stdout:
    print(line, end='')
    if "Application URL:" in line:
        # Extract the property ID from the URL
        url = line.strip().split("Application URL: ")[1]
        property_id = url.split("/")[-1]
        print(f"\nProperty ID: {property_id}")
        print(f"\nTo test, go to: http://localhost:3001/apply/{property_id}")
        break