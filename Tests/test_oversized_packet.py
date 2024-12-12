import socket


def oversized_packet_test(server_ip, port):
    """
    Sends an oversized DNS query to test packet size filtering.
    """
    oversized_data = b"A" * 1024  # Create a payload larger than 512 bytes
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Set a timeout to prevent hanging
        sock.settimeout(1)
        sock.sendto(oversized_data, (server_ip, port))
        print(f"Oversized packet sent to {server_ip}:{port}")
        response, _ = sock.recvfrom(512)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during oversized packet test: {e}")

    sock.close()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 53

    oversized_packet_test(SERVER_IP, SERVER_PORT)
