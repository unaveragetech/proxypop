import requests
from requests.exceptions import RequestException
from datetime import datetime
import argparse
from tqdm import tqdm
import time
from pythonping import ping
import socket
import json

# GeoIP API endpoint (example using a free GeoIP service)
GEOIP_API_URL = "https://ipapi.co/{}/json/"

# Function to test a single proxy with enhanced capabilities
def test_proxy(proxy_type, proxy_address, target_url, packet_count, ignore_response):
    proxy_url = f'socks{proxy_type}://{proxy_address}'
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    try:
        # Measure connection time (Speed Test)
        start_time = time.time()
        response = requests.get(target_url, proxies=proxies, timeout=10)
        connection_time = time.time() - start_time

        if response.status_code == 200:
            if not ignore_response:
                return True, response.json(), connection_time  # Successful connection, return response
            else:
                return True, "Response ignored", connection_time
    except RequestException as e:
        return False, str(e), None  # Return the error as a string
    return False, 'Unknown error', None

# Function to check proxy anonymity (Anonymity Check)
def check_proxy_anonymity(proxy_type, proxy_address):
    test_url = "http://httpbin.org/ip"  # URL that returns your IP
    proxy_url = f'socks{proxy_type}://{proxy_address}'
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            server_ip = response.json().get("origin")
            proxy_ip = proxy_address.split(':')[0]
            if proxy_ip in server_ip:
                return "Transparent"
            else:
                return "Elite/Anonymous"
    except RequestException:
        return "Unknown"
    return "Unknown"

# Function to perform GeoIP lookup
def geoip_lookup(ip):
    try:
        response = requests.get(GEOIP_API_URL.format(ip), timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_name"),
                "region": data.get("region"),
                "city": data.get("city"),
                "org": data.get("org")
            }
    except RequestException:
        return None
    return None

# Function to send multiple packets (Load Test)
def load_test(proxy_type, proxy_address, target_url, packet_count):
    proxy_url = f'socks{proxy_type}://{proxy_address}'
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    success_count = 0
    for _ in range(packet_count):
        try:
            response = requests.get(target_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                success_count += 1
        except RequestException:
            continue
    return success_count, packet_count

# Function to rotate proxies automatically
def rotate_proxies(proxies, target_url):
    for proxy, proxy_type in proxies:
        success, response, _ = test_proxy(proxy_type, proxy, target_url, 1, True)
        if success:
            yield proxy, proxy_type

# Function to read proxies from a file
def read_proxies(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

# Function to write results to files
def write_proxy_results(results, working_file='working_proxies.txt', invalid_file='invalid_proxies.txt'):
    with open(working_file, 'w') as wf, open(invalid_file, 'w') as inf:
        for result in results:
            if result['status'] == 'Success':
                wf.write(f"{result['proxy']} (Speed: {result['speed']}s, Anonymity: {result['anonymity']})\n")
            else:
                inf.write(f"{result['proxy']}\n")

# Function to write detailed results to a file
def write_detailed_results(results, output_file='proxy_test_results.txt'):
    with open(output_file, 'a') as file:
        file.write(f'\nTest Results - {datetime.now()}\n')
        file.write('-' * 40 + '\n')
        for result in results:
            file.write(f"Type: {result['type']}, Proxy: {result['proxy']}, Status: {result['status']}\n")
            if result['status'] == 'Success':
                file.write(f"  Response: {result['response']}\n")
                file.write(f"  Speed: {result['speed']} seconds\n")
                file.write(f"  Anonymity: {result['anonymity']}\n")
                if 'geoip' in result:
                    file.write(f"  GeoIP: {result['geoip']}\n")
            else:
                file.write(f"  Error: {result['error']}\n")
        file.write('-' * 40 + '\n\n')

# Function to perform a ping test
def ping_test(ip, count):
    try:
        response = ping(ip, count=count, timeout=2)
        return response.success(), response
    except Exception as e:
        return False, str(e)

# Function to display the list of proxies
def display_proxies(proxies, proxy_type):
    print(f"\n{proxy_type} Proxies:")
    print('-' * 40)
    for proxy in proxies:
        print(proxy)
    print('-' * 40)

# Main function for CLI
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Enhanced SOCKS4 & SOCKS5 Proxy Tester')
    parser.add_argument('--url', type=str, help='Minecraft server URL to test (e.g., http://example.com)', required=True)
    parser.add_argument('--show-proxies', action='store_true', help='Display the list of proxies')
    parser.add_argument('--output', type=str, help='Output file for test results', default='proxy_test_results.txt')
    parser.add_argument('--ping', action='store_true', help='Perform a ping test to the IP of the proxy')
    parser.add_argument('--packets', type=int, help='Number of packets to send when testing the proxy', default=1)
    parser.add_argument('--ignore-response', action='store_true', help='Ignore response when sending packets')
    parser.add_argument('--geoip', action='store_true', help='Perform GeoIP lookup for each proxy')
    parser.add_argument('--load-test', action='store_true', help='Enable load testing mode')
    
    args = parser.parse_args()
    target_url = args.url
    packet_count = args.packets
    ignore_response = args.ignore_response

    # Load proxies from files
    socks4_proxies = read_proxies('socks4.txt')
    socks5_proxies = read_proxies('socks5.txt')

    # Display proxies if requested
    if args.show_proxies:
        display_proxies(socks4_proxies, 'SOCKS4')
        display_proxies(socks5_proxies, 'SOCKS5')
        return

    # Aggregate proxies for testing
    all_proxies = [(proxy, '4') for proxy in socks4_proxies] + [(proxy, '5') for proxy in socks5_proxies]
    
    # Prepare to store results
    results = []

    # Use tqdm for the loading bar
    print(f"\nTesting proxies for URL: {target_url}\n")
    for proxy, proxy_type in tqdm(all_proxies, desc="Testing Proxies", unit="proxy"):
        ip, _ = proxy.split(':')  # Extract IP for ping test
        if args.ping:
            ping_success, ping_response = ping_test(ip, 4)
            print(f"\nPing Test to {ip}: {'Success' if ping_success else 'Failed'}")
            print(ping_response)

        # Test the proxy and capture results
        success, response, connection_time = test_proxy(proxy_type, proxy, target_url, packet_count, ignore_response)
        if success:
            anonymity = check_proxy_anonymity(proxy_type, proxy)
            geo_info = geoip_lookup(ip) if args.geoip else None

            result = {
                "type": f"SOCKS{proxy_type}",
                "proxy": proxy,
                "status": "Success",
                "response": response,
                "speed": round(connection_time, 3),
                "anonymity": anonymity,
                "geoip": geo_info
            }
        else:
            result = {
                "type": f"SOCKS{proxy_type}",
                "proxy": proxy,
                "status": "Failed",
                "error": response
            }
        
        # Append result to the list
        results.append(result)
    
    # Write detailed results
    write_detailed_results(results, args.output)

    # Summarize successful/failed proxies
    print("\nTest Summary:")
    working_proxies = [r for r in results if r['status'] == 'Success']
    invalid_proxies = [r for r in results if r['status'] == 'Failed']

    print(f"Working Proxies: {len(working_proxies)}")
    print(f"Invalid Proxies: {len(invalid_proxies)}")

    # Write summary results to separate files
    write_proxy_results(results)

if __name__ == '__main__':
    main()
