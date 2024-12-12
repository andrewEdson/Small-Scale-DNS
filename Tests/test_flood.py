import socket
import time
from dnslib import DNSRecord


def send_dns_query(server_ip, port, domain, num_queries, delay):
    """
    Sends a specified number of DNS queries to a server at a given interval.

    Args:
        server_ip (str): IP address of the DNS server.
        port (int): Port number of the DNS server (usually 53).
        domain (str): Domain name to query.
        num_queries (int): Number of queries to send.
        delay (float): Delay between queries in seconds.
    """
    query = DNSRecord.question(domain)

    for i in range(num_queries):
        try:
            # Create a new socket for each request to ensure continuation
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(1)  # Set a timeout to prevent hanging
                sock.sendto(query.pack(), (server_ip, port))
                response, _ = sock.recvfrom(512)
                print(f"Query {i + 1}: Response received")
        except Exception as e:
            print(f"Query {i + 1}: Failed with error {e}, continuing...")

        time.sleep(delay)


if __name__ == "__main__":
    # Server details
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 53
    DOMAIN = "example.com"  # The domain to query

    # Test parameters
    NUM_QUERIES = 100  # Total number of queries to send
    DELAY = 0.1  # Delay between queries in seconds (adjust to simulate load)

    print(
        f"Sending {NUM_QUERIES} queries to {SERVER_IP}:{SERVER_PORT} for domain {DOMAIN}"
    )
    send_dns_query(SERVER_IP, SERVER_PORT, DOMAIN, NUM_QUERIES, DELAY)
