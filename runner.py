# runner.py
import subprocess
import datetime
import logging
import os
import sys

# --- Optional: Load .env vars if needed ---
from dotenv import load_dotenv
load_dotenv()

# --- Logging setup ---
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, f"runner_{datetime.date.today()}.log")

# Configure logging: log to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def run_subprocess(label, command):
    logging.info(f"Starting: {label}")
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Finished: {label}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed: {label}")
        logging.error(str(e))
        sys.exit(1)

def main():
    logging.info("=== MCP Runner Pipeline Start ===")

    # Step 1: Run symbol discovery
    run_subprocess("Symbol Discovery", "python -m discovery.symbol_discovery")

    # Step 2: Launch containers for active symbols
    run_subprocess("Container Orchestration", "python -m orchestration.container_orchestration")

    # Future Step 3: Run strategy evaluator
    # run_subprocess("Strategy Evaluation", "python -m strategist.strategy_evaluator")

    # Future Step 4: Run LLM strategist (optional)
    # run_subprocess("LLM Strategist", "python -m strategist.mcp_llm_strategist")

    logging.info("=== MCP Runner Pipeline Complete ===\n")

if __name__ == "__main__":
    main()
