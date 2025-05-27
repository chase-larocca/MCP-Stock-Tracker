# MCP-Stock-Tracker/orchestration/container_orchestrator.py

import docker
import os
from db.db_connection import get_connection  

# Constants
IMAGE_NAME = "mcp-stock-tracker"
CONTAINER_PREFIX = "mcp-"

# Docker client
client = docker.from_env()

def get_active_symbols():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT symbol FROM tracked_symbols WHERE active = TRUE")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in results]

def container_exists(name):
    try:
        client.containers.get(name)
        return True
    except docker.errors.NotFound:
        return False
    
def get_inactive_symbols():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT symbol FROM tracked_symbols WHERE active = FALSE")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in results]

def cleanup_inactive_containers():
    inactive_symbols = get_inactive_symbols()
    print(f"[CLEANUP] Inactive symbols: {inactive_symbols}")

    for symbol in inactive_symbols:
        container_name = f"{CONTAINER_PREFIX}{symbol.lower()}"
        try:
            container = client.containers.get(container_name)
            print(f"[CLEANUP] Stopping and removing: {container_name}")
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            print(f"[CLEANUP] Container not found: {container_name} (already removed)")

def launch_container(symbol):
    container_name = f"{CONTAINER_PREFIX}{symbol.lower()}"
    if container_exists(container_name):
        print(f"[SKIP] Container already running: {container_name}")
        return

    print(f"[LAUNCH] Starting container for: {symbol}")

    client.containers.run(
        
        image=IMAGE_NAME,
        name=container_name,
        environment={
            "PYTHONUNBUFFERED": "1",
            "SYMBOL": symbol,
            "DB_HOST": os.getenv("DB_HOST", "192.168.1.202"),
            "DB_PORT": os.getenv("DB_PORT", "5432"),
            "DB_NAME": os.getenv("DB_NAME", "trading_db"),
            "DB_USER": os.getenv("DB_USER", "trading_user"),
            "DB_PASS": os.getenv("DB_PASS", "Blank-Salamander-Car2"),
            "BOT_VERSION": os.getenv("BOT_VERSION", "MCP-BOT:v0.0.1"),
            "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY", "8cd5d073ac044228b83f76d8166a3352"),

            "RISK_THRESHOLD": os.getenv("RISK_THRESHOLD", "0.5"),
            "CONFIDENCE_THRESHOLD": os.getenv("CONFIDENCE_THRESHOLD", "0.6"),
            "SIGNAL_STRENGTH_THRESHOLD": os.getenv("RISK_THRESHOLD", "0.4")
        },
        detach=True,
        restart_policy={"Name": "always"},
        network="mcp-stock-tracker_mcp-network"
    )

def main():
    cleanup_inactive_containers()      
    active_symbols = get_active_symbols()
    print(f"[INFO] Active symbols: {active_symbols}")
    for symbol in active_symbols:
        launch_container(symbol)

if __name__ == "__main__":
    main()
