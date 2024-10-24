
# **Advanced Proxy Testing Tool**

## **Overview**

This project is a comprehensive Proxy Testing Tool designed to evaluate and analyze the performance and reliability of various types of proxies: **SOCKS4**, **SOCKS5**, and **HTTP**. The tool can test proxies against a specified target URL, perform load tests, check anonymity, and provide detailed reports on proxy functionality. 

Ideal use cases include:

- Evaluating proxy reliability for web scraping.
- Testing proxies for accessing restricted content.
- Measuring speed and latency for gaming connections (e.g., Minecraft server testing).
- Assessing anonymity for secure browsing.

## **Features**

1. **Supports Multiple Proxy Types**:
   - SOCKS4 (from `socks4.txt`)
   - SOCKS5 (from `socks5.txt`)
   - HTTP (from `http.txt`)

2. **Flexible Testing Options**:
   - Custom target URL input for testing proxies.
   - Load testing mode to send multiple requests to the target URL.
   - Ignore responses from proxies if necessary.
   - Perform GeoIP lookups to get additional proxy location information.

3. **Detailed Reporting**:
   - Store working proxies in `working_proxies.txt`.
   - Save invalid proxies in `invalid_proxies.txt`.
   - Create detailed test reports in a customizable output file.
   - Track connection speeds, proxy anonymity levels, and more.

4. **User-friendly Command Line Interface (CLI)**:
   - View proxy lists before testing.
   - Control various options directly from the command line.
   - Progress bar with `tqdm` to show testing progress.

5. **Ping and Connectivity Tests**:
   - Ping the IP of the proxy for latency checks.
   - Evaluate packet delivery success.

6. **Load Testing & Packet Sending**:
   - Configure packet count for load tests.
   - Toggle response ignoring for rapid-fire tests.

## **Installation**

### **Prerequisites**
- Python 3.8 or above.
- Pip package manager.

### **Installing Dependencies**
To install the required Python packages, navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- `requests`: For HTTP requests and proxy connections.
- `pythonping`: For ping and latency checks.
- `tqdm`: For the progress bar functionality in the command line.

## **Usage**

### **Command Line Options**
This script is controlled entirely from the command line, providing flexibility in proxy testing. Below are the available options:

```bash
python proxy_tester.py --url <target_url> [options]
```

### **Available Arguments**
| Argument                | Description                                                                                     | Required | Example                                    |
|-------------------------|------------------------------------------------------------------------------------------------|----------|--------------------------------------------|
| `--url`                  | Target URL to test the proxies against.                                                        | Yes      | `--url http://example.com`                 |
| `--show-proxies`         | Displays the list of all proxies loaded from `socks4.txt`, `socks5.txt`, and `http.txt`.       | No       | `--show-proxies`                           |
| `--output`               | Specify a file to save detailed test results. Default is `proxy_test_results.txt`.             | No       | `--output results.txt`                     |
| `--ping`                 | Enables a ping test to the IP addresses of the proxies.                                        | No       | `--ping`                                   |
| `--packets`              | Number of packets to send for load testing. Default is `1`.                                    | No       | `--packets 10`                             |
| `--ignore-response`      | Ignore responses when sending packets to proxies (speed up testing).                           | No       | `--ignore-response`                        |
| `--geoip`                | Perform GeoIP lookups for proxies to get additional location data.                             | No       | `--geoip`                                  |
| `--load-test`            | Enables load testing mode, sending multiple packets to the target URL.                         | No       | `--load-test`                              |

### **Examples**
1. **Basic Test for Minecraft Server**:
   ```bash
   python proxy_tester.py --url http://minecraft.example.com
   ```
   
2. **View All Loaded Proxies**:
   ```bash
   python proxy_tester.py --show-proxies
   ```

3. **Test with Load Testing and GeoIP Lookup**:
   ```bash
   python proxy_tester.py --url http://example.com --load-test --packets 5 --geoip
   ```

4. **Perform a Ping Test with Ignored Responses**:
   ```bash
   python proxy_tester.py --url http://example.com --ping --ignore-response
   ```

5. **Save Results to a Custom File**:
   ```bash
   python proxy_tester.py --url http://example.com --output custom_results.txt
   ```

## **Files and Directory Structure**

```
/project-directory
    ├── proxy_tester.py           # The main proxy testing script
    ├── requirements.txt          # List of required Python packages
    ├── socks4.txt                # Contains SOCKS4 proxies (format: IP:PORT)
    ├── socks5.txt                # Contains SOCKS5 proxies (format: IP:PORT)
    ├── http.txt                  # Contains HTTP proxies (format: IP:PORT)
    ├── working_proxies.txt       # Output file for all working proxies
    ├── invalid_proxies.txt       # Output file for invalid/non-working proxies
    └── proxy_test_results.txt    # Detailed test results log
```

### **Proxy Files Format**
Each proxy should be in the format `IP:PORT`, with one proxy per line. Example for `socks4.txt`:

```
192.168.0.1:1080
203.0.113.5:1080
198.51.100.9:1080
```

## **Functions Explained**

### **Core Functions**

1. **Proxy Testing (`test_proxy`)**:
   - Tests a proxy by attempting to access the specified target URL.
   - Measures the connection time and validates response codes.
   - Returns detailed data, including response content and speed.

2. **Anonymity Check (`check_proxy_anonymity`)**:
   - Determines the anonymity of a proxy.
   - Uses an external service to check if the proxy's IP is visible.

3. **Load Testing (`load_test`)**:
   - Sends multiple requests to the target URL through a proxy.
   - Tracks successful packet delivery for proxy performance.

4. **Ping Test (`ping_test`)**:
   - Performs a ping to the proxy's IP address.
   - Measures the response time and success rate.

5. **GeoIP Lookup (`geoip_lookup`)**:
   - Uses a public GeoIP API to fetch the location data of a proxy.
   - Includes details like country, region, city, and organization.

### **Advanced Features**

- **Load Test & Packet Sending**: Evaluate proxy robustness by sending multiple packets. Toggle to ignore responses to speed up testing.
- **Proxy Rotation**: Automatically switch between proxies when running multiple tests.
- **Detailed Logging**: All test results are logged, including both working and non-working proxies, for later review.

## **Troubleshooting**

### **Common Issues**

1. **Proxy Connection Timeout**:
   - Increase the timeout duration in the `requests.get` function.
   - Check proxy availability and validity.

2. **Permission Errors**:
   - Ensure you have read/write access to the directory.
   - Run the script with appropriate permissions (`sudo` if necessary).

3. **Invalid Proxy Format**:
   - Ensure proxies in the text files follow the `IP:PORT` format without additional characters or spaces.

### **Debugging Tips**
- Use the `--show-proxies` option to check if proxies are loaded correctly.
- Run a smaller packet count first with `--packets 1` to ensure basic functionality.
- Use the `--ping` option to verify proxy IP connectivity before full tests.

## **Future Enhancements**

- **Proxy Caching**: Implement a database or cache system to store results of previously tested proxies.
- **GUI Interface**: Build a simple interface for users unfamiliar with the command line.
- **Multi-threading**: Speed up testing by testing multiple proxies simultaneously.

## **Contributing**

Contributions are welcome! Please feel free to open an issue or submit a pull request for any suggestions, bug fixes, or improvements.

## **License**

This project is licensed under the MIT License - see the `LICENSE` file for details.

## **Contact**

For questions or further information, please reach out to the project maintainer.

