import threading
import time
import requests
import subprocess
import random
import logging
import json
from flask import Flask, request, jsonify
from scapy.all import sniff, IP, TCP, UDP, Raw

# Configure logging
logging.basicConfig(filename='network_tool.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Global variable to hold instances
instances = []
results_data = {}  # To store results for exporting

app = Flask(__name__)

# Function to log and track results
def log_result(instance_port, action, result):
    global results_data
    if instance_port not in results_data:
        results_data[instance_port] = []
    results_data[instance_port].append({"action": action, "result": result})

# Function to simulate sending packets
def send_packets(target, rate, amount, instance_port):
    for _ in range(amount):
        time.sleep(1 / rate)  # Control the sending rate
        # Simulate packet sending to the target
        packet_sent = f"Packet sent to {target}: {random.randint(1, 100)}"
        logging.info(packet_sent)
        log_result(instance_port, "send_packets", packet_sent)

# Function to ping a URL
def ping(target, instance_port):
    try:
        response = subprocess.run(['ping', '-c', '1', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = response.stdout.decode() if response.returncode == 0 else response.stderr.decode()
        log_result(instance_port, "ping", result)
        return result
    except Exception as e:
        return str(e)

# Sniffer function
def packet_sniffer(interface, instance_port):
    def process_packet(packet):
        if IP in packet:
            src = packet[IP].src
            dst = packet[IP].dst
            protocol = packet[IP].proto
            packet_info = f"Packet: {src} -> {dst}, Protocol: {protocol}"
            logging.info(packet_info)
            log_result(instance_port, "packet_sniffer", packet_info)

    sniff(iface=interface, prn=process_packet, store=0)  # Sniff packets and call process_packet for each

# Endpoint to start sending packets
@app.route('/start', methods=['POST'])
def start_sending():
    data = request.json
    target = data.get('target')
    rate = data.get('rate', 1)
    amount = data.get('amount', 10)
    
    threading.Thread(target=send_packets, args=(target, rate, amount, 5000)).start()  # Assuming main instance is on port 5000
    return jsonify({"message": "Packet sending started", "target": target, "rate": rate, "amount": amount})

# Endpoint to ping a URL
@app.route('/ping', methods=['POST'])
def ping_url():
    data = request.json
    target = data.get('target')
    instance_port = request.host.split(':')[-1]  # Get the instance port from the request

    ping_result = ping(target, instance_port)
    return jsonify({"message": f"Ping result for {target}", "result": ping_result})

# Endpoint to start packet sniffing
@app.route('/sniff', methods=['POST'])
def start_sniffing():
    data = request.json
    interface = data.get('interface', 'lo')  # Default to loopback
    instance_port = request.host.split(':')[-1]
    
    # Start sniffing in a separate thread
    threading.Thread(target=packet_sniffer, args=(interface, instance_port)).start()
    return jsonify({"message": f"Packet sniffing started on {interface}."})

# Function to create a new Flask instance
def create_instance(port):
    new_app = Flask(__name__)

    @new_app.route('/mirror', methods=['GET'])
    def mirror():
        return jsonify({"message": f"Connected to mirror instance on port {port}"})

    @new_app.route('/ping', methods=['POST'])
    def instance_ping():
        data = request.json
        target = data.get('target')
        instance_port = port
        ping_result = ping(target, instance_port)
        return jsonify({"message": f"Ping result for {target}", "result": ping_result})

    @new_app.route('/start', methods=['POST'])
    def instance_start_sending():
        data = request.json
        target = data.get('target')
        rate = data.get('rate', 1)
        amount = data.get('amount', 10)
        threading.Thread(target=send_packets, args=(target, rate, amount, port)).start()
        return jsonify({"message": "Packet sending started", "target": target, "rate": rate, "amount": amount})

    @new_app.route('/sniff', methods=['POST'])
    def instance_start_sniffing():
        data = request.json
        interface = data.get('interface', 'lo')  # Default to loopback
        packet_sniffer(interface, port)
        return jsonify({"message": f"Packet sniffing started on {interface}."})

    new_app.run(port=port)

# CLI function to manage instances
def cli():
    while True:
        command = input("Enter command (start_instance, list_instances, ping, send_packet, start_sniffing, export_results, exit): ")
        
        if command == "start_instance":
            port = len(instances) + 5000  # Simple port allocation starting from 5000
            instance_thread = threading.Thread(target=create_instance, args=(port,))
            instance_thread.start()
            instances.append(port)
            print(f"Started instance on port {port}")

        elif command == "list_instances":
            print("Running instances:", instances)

        elif command == "ping":
            target = input("Enter URL to ping: ")
            results = []
            for port in instances:
                response = requests.post(f'http://127.0.0.1:{port}/ping', json={"target": target})
                results.append(f"Instance on port {port}: {response.json()}")
            print("\n".join(results))

        elif command == "send_packet":
            target = input("Enter URL to send packets to: ")
            rate = float(input("Enter send rate (packets per second): "))
            amount = int(input("Enter total packets to send: "))
            results = []
            for port in instances:
                response = requests.post(f'http://127.0.0.1:{port}/start', json={"target": target, "rate": rate, "amount": amount})
                results.append(f"Instance on port {port}: {response.json()}")
            print("\n".join(results))

        elif command == "start_sniffing":
            interface = input("Enter network interface to sniff on (e.g., eth0, lo): ")
            results = []
            for port in instances:
                response = requests.post(f'http://127.0.0.1:{port}/sniff', json={"interface": interface})
                results.append(f"Instance on port {port}: {response.json()}")
            print("\n".join(results))

        elif command == "export_results":
            with open('results.json', 'w') as f:
                json.dump(results_data, f)
            print("Results exported to results.json")

        elif command == "exit":
            break

        else:
            print("Unknown command.")

if __name__ == '__main__':
    # Start the main Flask app
    threading.Thread(target=app.run, kwargs={'port': 5000}).start()
    # Start the CLI interface
    cli()
