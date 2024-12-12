import socketserver
import time
from dnslib import DNSRecord, QTYPE, RCODE, RR, A
from collections import defaultdict


class DNSHandler(socketserver.BaseRequestHandler):
    ALLOWED_DOMAINS = {
        "example.com": "1.2.3.4",  # Test domain
        "google.com": "8.8.8.8",  # Real domain
        "bbc.co.uk": "17.142.160.1",  # Real domain
        "ebay.com": "13.107.21.200",  # Real domain
    }  # Allowed domains
    LOGGED_QUERIES = set()  # Keep track of logged queries

    # Cache structure to store responses with their expiration times
    CACHE = defaultdict(lambda: {"response": None, "expires": 0})
    CACHE_TTL = 300  # Time-to-live for cache entries in seconds

    RATE_LIMIT = 10  # Maximum requests allowed per IP in the time window
    TIME_WINDOW = 10  # Time window in seconds
    BLOCK_DURATION = 30  # Duration to block an IP in seconds
    request_log = {}  # Tracks request timestamps per IP
    blocked_ips = {}  # Tracks blocked IPs with unblock time

    def handle(self):
        data, socket = self.request
        client_address = self.client_address[0]
        current_time = time.time()

        # Check if the IP is currently blocked
        if client_address in self.blocked_ips:
            if current_time < self.blocked_ips[client_address]:
                print(f"Blocked request from {client_address}")
                return  # Ignore requests from blocked IPs
            else:
                # Unblock the IP after the block duration
                del self.blocked_ips[client_address]

        # Rate limit check
        self.request_log.setdefault(client_address, [])
        request_times = self.request_log[client_address]

        # Remove timestamps outside the time window
        self.request_log[client_address] = [
            timestamp
            for timestamp in request_times
            if current_time - timestamp < self.TIME_WINDOW
        ]

        # Check if the number of requests exceeds the rate limit
        if len(self.request_log[client_address]) >= self.RATE_LIMIT:
            self.blocked_ips[client_address] = current_time + self.BLOCK_DURATION
            print(f"IP {client_address} blocked due to rate limit")
            return

        # Log the current request
        self.request_log[client_address].append(current_time)

        try:
            dns_request = DNSRecord.parse(data)
            question = dns_request.questions[0]
            qname = str(question.qname).rstrip(".")
            qtype = QTYPE[question.qtype]

            # Ignore reverse DNS (PTR) queries or other unwanted types
            if qtype == "PTR" or qname.endswith(".arpa"):
                return  # Skip PTR queries

            # Check cache for response
            cache_key = (qname, qtype)
            cached_response = self.CACHE[cache_key]

            if (
                cached_response["response"]
                and cached_response["expires"] > current_time
            ):
                response = cached_response["response"]
                print(f"Cache hit for {qname}")
            else:
                print(f"Cache miss for {qname}")
                # Respond only to allowed domains for A records
                if qname in self.ALLOWED_DOMAINS and qtype == "A":
                    ip = self.ALLOWED_DOMAINS[qname]
                    response = self.create_response(dns_request, ip)
                else:
                    response = self.create_response(dns_request, None)

                # Update cache with new response
                self.CACHE[cache_key] = {
                    "response": response,
                    "expires": current_time + self.CACHE_TTL,
                }

            print(f"Received query from {client_address}: {qname}")
            self.LOGGED_QUERIES.add((client_address, qname))

            # Send the response back to the client
            socket.sendto(response.pack(), self.client_address)
        except Exception as e:
            print(f"Error handling request: {e}")

    def create_response(self, request, ip):
        response = request.reply()
        response.rr = []  # Clear existing answers
        if ip:
            response.add_answer(
                RR(rname=request.q.qname, rtype=QTYPE.A, rclass=1, ttl=300, rdata=A(ip))
            )
        else:
            response.header.rcode = RCODE.NXDOMAIN
        return response


class SafeUDPServer(socketserver.UDPServer):
    def verify_request(self, request, client_address):
        data, _ = request
        if len(data) > 512:  # Reject oversized packets
            print(f"Dropped oversized packet from {client_address}")
            return False

        # Verify RD flag is set to prevent abuse
        try:
            dns_request = DNSRecord.parse(data)
            if not dns_request.header.rd:
                print(f"Dropped non-recursive query from {client_address}")
                return False
        except Exception as e:
            print(f"Error parsing DNS request from {client_address}: {e}")
            return False

        return True


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 53
    print(f"Starting DNS server on {HOST}:{PORT}")
    with SafeUDPServer((HOST, PORT), DNSHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down DNS server.")
            server.shutdown()
