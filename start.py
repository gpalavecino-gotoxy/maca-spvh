import os
import subprocess
import sys

port = os.environ.get("PORT", "8501")
env = os.environ.copy()
env["STREAMLIT_SERVER_PORT"] = port

result = subprocess.run(
    ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.headless=true"],
    env=env,
)
sys.exit(result.returncode)
