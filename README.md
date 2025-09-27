# Small-Scale-DNS-Server

DNS server with common security practices

## Overview

This is a secure DNS server implementation that includes various security features such as:

- Rate limiting to prevent flooding attacks
- Caching with TTL (Time-To-Live) management
- Domain whitelist filtering
- Recursive query validation (RD flag checking)
- Input validation and oversized packet protection
- Cache poisoning prevention

## Prerequisites

Before running the DNS server or tests, make sure you have Python 3.x installed with the following dependencies:

```bash
pip install dnslib
```

## Running the DNS Server

### Standard Operation

To start the DNS server on the default port (53):

```bash
cd Server
python DNS.py
```

**Note:** Running on port 53 requires administrator/root privileges since it's a privileged port.

### For Testing (Non-privileged port)

If you want to test without administrator privileges, you can modify the port in the `DNS.py` file:

1. Open `Server/DNS.py`
2. Change `PORT = 53` to a higher port like `PORT = 5353`
3. Run: `python DNS.py`

The server will start and display:

```
Starting DNS server on 0.0.0.0:53
```

## Testing the DNS Server

The project includes several test scripts in the `Tests/` directory to validate different security features:

### Available Tests

1. **Rate Limiting Test** (`test_flood.py`)

   - Tests the server's ability to handle flooding attacks
   - Sends multiple rapid queries to trigger rate limiting

2. **Recursive Query Test** (`test_rd.py`)

   - Tests that the server only accepts recursive queries (RD flag set)
   - Sends non-recursive queries that should be rejected

3. **Cache Poisoning Test** (`test_cache_poisoning.py`)

   - Tests the server's resistance to cache poisoning attacks

4. **Invalid Data Test** (`test_invalid_data.py`)

   - Tests the server's handling of malformed DNS packets

5. **Oversized Packet Test** (`test_oversized_packet.py`)
   - Tests the server's handling of oversized DNS packets

### Running Individual Tests

To run a specific test:

```bash
cd Tests
python test_flood.py
python test_rd.py
python test_cache_poisoning.py
python test_invalid_data.py
python test_oversized_packet.py
```

### Running All Tests

To run all tests sequentially, you can create a simple batch script or run them one by one.

**For Windows (PowerShell):**

```powershell
cd Tests
Get-ChildItem -Name "test_*.py" | ForEach-Object { python $_ }
```

**For Linux/Mac:**

```bash
cd Tests
for test in test_*.py; do python "$test"; done
```

## Server Configuration

The DNS server includes several configurable parameters in `DNS.py`:

- **ALLOWED_DOMAINS**: Whitelist of domains the server will resolve
- **CACHE_TTL**: Time-to-live for cached responses (default: 300 seconds)
- **RATE_LIMIT**: Maximum requests per IP in the time window (default: 10)
- **TIME_WINDOW**: Rate limiting time window in seconds (default: 10)
- **BLOCK_DURATION**: How long to block IPs that exceed rate limit (default: 30 seconds)

## Testing Against the Server

Once the server is running, you can test it with standard DNS tools:

```bash
# Using nslookup
nslookup example.com 127.0.0.1

# Using dig
dig @127.0.0.1 example.com

# Using host
host example.com 127.0.0.1
```

## Stopping the Server

To stop the DNS server, press `Ctrl+C` in the terminal where it's running. The server will display:

```
Shutting down DNS server.
```

## Security Features

- **Domain Filtering**: Only resolves whitelisted domains
- **Rate Limiting**: Prevents flooding attacks by limiting requests per IP
- **Input Validation**: Validates DNS packet structure and size
- **Cache Management**: Implements secure caching with TTL
- **Recursive Query Validation**: Only accepts properly formed recursive queries
