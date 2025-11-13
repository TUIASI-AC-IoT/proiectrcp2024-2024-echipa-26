# RIPv2 Router Implementation

A complete implementation of the RIPv2 (Routing Information Protocol version 2) routing protocol in Python, containerized with Docker for easy deployment and testing.

## Project Structure

```
.
├── src/                    # Python source code
│   ├── main.py            # Application entry point
│   ├── Router.py          # Main router implementation
│   ├── Message.py         # RIP message handling
│   ├── RIPEntry.py        # RIP routing entry
│   ├── SharedTable.py     # Routing table management
│   ├── Timer.py           # RIP timers (update, timeout, garbage collection)
│   ├── CLI.py             # Command-line interface
│   └── define.py          # Constants and definitions
├── docker/                 # Docker configuration
│   ├── Dockerfile         # Container image definition
│   ├── docker-compose.yaml # Multi-container orchestration
│   ├── entrypoint.sh      # Container startup script
│   └── .dockerignore      # Docker ignore patterns
├── scripts/                # Utility scripts
│   └── docker-run.sh      # Quick start script for Docker operations
├── cfg/                    # Router configuration files
│   ├── r1/                # Router 1 configs
│   ├── r2/                # Router 2 configs
│   └── ...                # Additional router configs
├── docs/                   # Documentation
│   ├── README.md          # Detailed documentation (in Romanian)
│   ├── Images/            # Diagrams and screenshots
│   └── TODO               # Project TODO list
└── README.md              # This file

```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Linux host with networking capabilities
- Wireshark (optional, for packet capture analysis)

### Running the Network

```bash
# Build the router images
./scripts/docker-run.sh build

# Start all routers
./scripts/docker-run.sh start

# Check status
./scripts/docker-run.sh status

# View logs from a specific router
./scripts/docker-run.sh logs r1

# Access router CLI
./scripts/docker-run.sh cli r1

# Capture network traffic
./scripts/docker-run.sh capture r1

# Stop all routers
./scripts/docker-run.sh stop
```

## Features

- **RIPv2 Protocol Implementation**
  - Distance-vector routing algorithm (Bellman-Ford)
  - Support for VLSM and CIDR
  - Multicast updates to 224.0.0.9
  - Split horizon with poison reverse
  - Route timeouts and garbage collection

- **Interactive CLI**
  - View routing tables
  - Search routes
  - Browse network topology
  - Monitor router status
  - Real-time updates

- **Docker Integration**
  - 10 pre-configured routers
  - Multiple isolated networks using ipvlan
  - Automatic network topology setup
  - Easy deployment and testing

- **Network Analysis**
  - Built-in packet capture functionality
  - Wireshark-compatible pcap output
  - Traffic filtering capabilities

## Network Topology

The implementation includes 10 routers (R1-R10) connected across multiple networks forming a complex topology. See [docs/Images/Topologie.png](docs/Images/Topologie.png) for the complete network diagram.

### Docker vs VirtualBox Networking

This is an updated Docker version of the original VirtualBox implementation. Due to Docker's network validation requirements, some network configurations have been modified:

- **Original VirtualBox**: Used `192.168.4.0/22` which encompasses addresses from `192.168.4.0` to `192.168.7.255`
- **Docker Version**: Changed to `192.168.4.0/24` (only `192.168.4.0` to `192.168.4.255`)

**Reason for Change**: Docker's networking layer performs strict subnet overlap checking and prevents the creation of networks with overlapping address spaces. Since the topology also uses `192.168.5.0/24`, Docker detects a collision with `192.168.4.0/22` (which would include the 192.168.5.x range) and refuses to create the networks. This validation cannot be bypassed in Docker.

**Key Difference**: VirtualBox uses independent, isolated networks for each interface, allowing overlapping address spaces without conflict. Docker uses a shared networking subsystem that must maintain globally unique subnet allocations across all containers and networks on the host.

The functionality and routing behavior remain identical - only the subnet mask on this one network needed adjustment to satisfy Docker's requirements.

## Documentation

For detailed documentation about RIPv2 protocol, implementation details, and usage instructions (in Romanian), see [docs/README.md](docs/README.md).

## Available Commands

Use `./scripts/docker-run.sh help` to see all available commands:

- `build` - Build Docker images
- `start` - Start all routers (detached)
- `start-fg` - Start in foreground
- `stop` - Stop all routers
- `restart` - Restart all routers
- `logs [router]` - Follow logs
- `status` - Show container status
- `shell [router]` - Open shell in container
- `cli [router]` - Access router CLI
- `capture [router] [filter]` - Capture packets
- `clean` - Remove all containers and images
- `rebuild` - Clean rebuild
- `test` - Run connectivity tests

## Development

The project is organized for easy development and maintenance:

- All Python source code is in `src/`
- Docker configuration is isolated in `docker/`
- Scripts for automation are in `scripts/`
- Documentation and images are in `docs/`
- Router configs are in `cfg/`

## License

Academic project - TUIASI AC IoT 2024

## Contributors

Team 26 - RCP Project 2024
