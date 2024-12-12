import socket


def invalid_data_test(server_ip, port):
    """
    Sends a malformed DNS query to test server robustness.
    """
    malformed_data = b"\x00\x00\x00\x00"  # Invalid DNS query data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Set a timeout to prevent hanging
        sock.settimeout(1)
        sock.sendto(malformed_data, (server_ip, port))
        print("Malformed query sent.")
        response, _ = sock.recvfrom(512)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during malformed query test: {e}")

    sock.close()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 53

    invalid_data_test(SERVER_IP, SERVER_PORT)
