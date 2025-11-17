import subprocess
import sys
import os

num_instances = 2

# Path to the Python interpreter in the virtual environment (Windows)
venv_python = os.path.join(".venv", "Scripts", "python.exe")

for _ in range(num_instances):
    subprocess.Popen([venv_python, "main.py"])
