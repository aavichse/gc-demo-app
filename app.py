from flask import Flask, request, jsonify
import os
import threading
import time
import requests
import sys
import logging
from datetime import datetime

app = Flask(__name__)


# Disable Flask's default logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Set to ERROR to suppress default logs

# Global variable to store the counter for each thread
counters = {}

# mapping from hostname to IP 
hosts_file_path='hosts.txt'
hosts_mapping = {}
last_modified_time = 0

def load_hosts_file():
    global hosts_mapping, last_modified_time
    if not os.path.exists(hosts_file_path):
        LOG(f"Hosts file {hosts_file_path} not found.")
        return

    current_modified_time = os.path.getmtime(hosts_file_path)

    if current_modified_time != last_modified_time:
        LOG(f"Reloading hosts file {hosts_file_path}...")
        hosts_mapping = {}  # Clear the old mapping
        with open(hosts_file_path, 'r') as f:
            for line in f:
                if line.strip():
                    hostname, ip = line.split()
                    hosts_mapping[hostname] = ip
        last_modified_time = current_modified_time  # Update the last modified time
        LOG(f"Hosts file loaded: {hosts_mapping}")
    else:
        LOG(f"Hosts file {hosts_file_path} has not changed. Skipping reload.")


def resolve_target(target):
    if ':' in target:
        address, port = target.split(':')
        resolved_address = hosts_mapping.get(address, address)
        return f"{resolved_address}:{port}"
    else:
        return hosts_mapping.get(target, target)


def timestamp():
    return datetime.now().strftime('%H:%M:%S')


def LOG(msg:str): 
    print(f'{timestamp()} -- {msg}', file=sys.stderr)


def send_request_to_target(target: str, app_id: str, interval: int):
    """Send a request to the target every second with the format /echo/<app_id>/<counter>."""
    counter = 0
    url = ""
    
    while True:
        try:
            load_hosts_file()  
            resolved_target = resolve_target(target)
            url = f"http://{resolved_target}/echo/{app_id}/{counter}"
            LOG(f"CLIENT/{target} SEND --> {counter=}   |  {resolved_target=}")
            response = requests.get(url)
            LOG(f"CLIENT/{target} RECV <-- {response.text}")
        except Exception as e:
            LOG(f"ERROR: sending request to {url}: {e}")
        
        # Increment counter and wait for 1 second
        counter += 1
        time.sleep(interval)

@app.route('/echo/<src_id>/<counter>', methods=['GET'])
def echo(src_id, counter):
    app_id = os.getenv('APP_ID', 'unknown')
    LOG(f"SERVER: GET {request.path}")
    message = f"ACK {app_id} : counter={counter}"
    return message

def start_sending_requests():
    """Start a separate thread for each target."""
    targets = os.getenv('TARGETS', '').split(',')
    app_id = os.getenv('APP_ID', 'unknown')
    
    for target in targets:
        if target:
            # Parse the target and interval
            if '#' in target:
                target, interval_str = target.split('#')
                interval = int(interval_str)
            else:
                interval = 1  # Default interval is 1 second

            LOG(f"Starting thread for target {target} with interval {interval} seconds")
            thread = threading.Thread(target=send_request_to_target, args=(target, app_id, interval))
            thread.daemon = True
            thread.start()


if __name__ == "__main__":
    load_hosts_file()
    # Start sending requests to targets in the background
    start_sending_requests()
    
    # Set the port to 8000 by default
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

