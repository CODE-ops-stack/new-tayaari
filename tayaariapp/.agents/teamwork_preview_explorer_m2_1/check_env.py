import sys
import subprocess

print("Python version:", sys.version)

packages_to_check = [
    "spacy",
    "nltk",
    "pydantic",
    "google.genai",
    "google.generativeai",
    "requests",
    "dotenv",
    "pytest",
    "regex"
]

for pkg in packages_to_check:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "available")
        print(f"  {pkg}: INSTALLED ({ver})")
    except Exception as e:
        print(f"  {pkg}: NOT AVAILABLE ({e})")

print("\nPip list:")
try:
    res = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    print(res.stdout[:2000])
except Exception as e:
    print("pip list error:", e)
