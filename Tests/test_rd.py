import socket
import struct


def build_dns_query(domain, recursive=False):
    """
    Manually builds a DNS query packet.

    Args:
        domain (str): The domain name to query.
        recursive (bool): Whether the query should be recursive.

    Returns:
        bytes: The DNS query in bytes.
    """
    # DNS Header: ID (2 bytes), Flags (2 bytes), QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT (2 bytes each)
    transaction_id = 0x1234  # Random ID for the query
    flags = (
        0x0100 if recursive else 0x0000
    )  # Set recursion desired (RD) if recursive=True
    qdcount = 1  # One question
    ancount = 0  # No answers (query)
    nscount = 0  # No name server records
    arcount = 0  # No additional records

    header = struct.pack(
        ">HHHHHH", transaction_id, flags, qdcount, ancount, nscount, arcount
    )

    # DNS Question Section: QNAME (variable), QTYPE (2 bytes), QCLASS (2 bytes)
    qname = (
        b"".join(
            len(part).to_bytes(1, "big") + part.encode() for part in domain.split(".")
        )
        + b"\x00"
    )
    qtype = 1  # Type A (host address)
    qclass = 1  # Class IN (Internet)

    question = qname + struct.pack(">HH", qtype, qclass)

    return header + question


def non_recursive_query_test(server_ip, port, domain):
    """
    Sends a manually constructed non-recursive DNS query.
    """

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Socket timeout
        sock.settimeout(1)
        # Build the DNS query
        query = build_dns_query(domain, recursive=False)

        # Send the query
        sock.sendto(query, (server_ip, port))
        print(f"Non-recursive query sent for domain: {domain}")

        # Receive and parse the response
        response, _ = sock.recvfrom(512)
        print(f"Response (raw bytes): {response}")
    except Exception as e:
        print(f"Error during non-recursive query test: {e}")
    finally:
        if sock:
            sock.close()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"  # Local DNS server
    SERVER_PORT = 53  # Non-standard port for testing
    DOMAIN = "example.com"  # Test domain

    non_recursive_query_test(SERVER_IP, SERVER_PORT, DOMAIN)
