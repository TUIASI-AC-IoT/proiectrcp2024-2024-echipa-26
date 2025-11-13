#!/bin/bash

# Quick start script for RIPv2 Docker implementation

set -e

# Change to project root directory
cd "$(dirname "$0")/.."

COMMAND=${1:-"help"}

case "$COMMAND" in
    build)
        echo "Building RIPv2 router images..."
        docker-compose -f docker/docker-compose.yaml build
        echo "Build complete!"
        ;;

    start)
        echo "Starting all RIPv2 routers..."
        docker-compose -f docker/docker-compose.yaml up -d
        echo "All routers started!"
        echo "View logs with: ./scripts/docker-run.sh logs"
        ;;

    start-fg)
        echo "Starting all RIPv2 routers in foreground..."
        docker-compose -f docker/docker-compose.yaml up
        ;;

    stop)
        echo "Stopping all RIPv2 routers..."
        docker-compose -f docker/docker-compose.yaml down
        echo "All routers stopped!"
        ;;

    restart)
        echo "Restarting all RIPv2 routers..."
        docker-compose -f docker/docker-compose.yaml restart
        echo "All routers restarted!"
        ;;

    logs)
        ROUTER=${2:-""}
        if [ -z "$ROUTER" ]; then
            echo "Following logs from all routers (Ctrl+C to exit)..."
            docker-compose -f docker/docker-compose.yaml logs -f
        else
            echo "Following logs from router $ROUTER (Ctrl+C to exit)..."
            docker-compose -f docker/docker-compose.yaml logs -f "$ROUTER"
        fi
        ;;

    status)
        echo "Router container status:"
        docker-compose -f docker/docker-compose.yaml ps
        ;;

    shell)
        ROUTER=${2:-"r1"}
        echo "Opening shell in router $ROUTER..."
        docker exec -it "ripv2-$ROUTER" bash
        ;;

    cli)
        ROUTER=${2:-"r1"}
        echo "Accessing CLI of router $ROUTER..."
        docker attach "ripv2-$ROUTER"
        ;;

    clean)
        echo "Removing all containers, networks, and images..."
        docker-compose -f docker/docker-compose.yaml down --volumes --rmi all
        echo "Cleanup complete!"
        ;;

    rebuild)
        echo "Rebuilding and restarting all routers..."
        docker-compose -f docker/docker-compose.yaml down
        docker-compose -f docker/docker-compose.yaml build --no-cache
        docker-compose -f docker/docker-compose.yaml up -d
        echo "Rebuild complete!"
        ;;

    test)
        echo "Testing RIPv2 network setup..."
        echo ""
        echo "1. Checking if containers are running..."
        docker-compose -f docker/docker-compose.yaml ps
        echo ""
        echo "2. Testing connectivity between R1 and R2..."
        docker exec ripv2-r1 ping -c 3 192.168.1.2 || echo "Connectivity test failed!"
        echo ""
        echo "3. Checking RIP multicast traffic on R1..."
        timeout 10 docker exec ripv2-r1 tcpdump -i any -c 5 udp port 520 || echo "No RIP traffic detected yet"
        ;;

    capture)
        ROUTER=${2:-"r1"}
        FILTER=${3:-"port 520"}
        FILENAME="capture_${ROUTER}_$(date +%Y%m%d_%H%M%S).pcap"
        CONTAINER="ripv2-$ROUTER"
        CLEANUP_DONE=0

        echo "Starting packet capture on router $ROUTER..."
        echo "Filter: $FILTER"
        echo "Output file: $FILENAME"
        echo ""
        echo "Press Ctrl+C to stop capturing..."
        echo ""

        # Function to cleanup and copy file
        cleanup_and_copy() {
            # Prevent double execution
            if [ "$CLEANUP_DONE" -eq 1 ]; then
                return
            fi
            CLEANUP_DONE=1

            echo ""
            echo "Stopping capture..."

            # Kill tcpdump gracefully - send SIGTERM to all tcpdump processes
            docker exec "$CONTAINER" sh -c "killall -TERM tcpdump 2>/dev/null || true" >/dev/null 2>&1

            # Wait for tcpdump to flush and close file
            sleep 3

            # Copy the file
            if docker cp "$CONTAINER:/app/logs/$FILENAME" "./$FILENAME" 2>/dev/null; then
                SIZE=$(stat -c%s "./$FILENAME" 2>/dev/null || stat -f%z "./$FILENAME" 2>/dev/null || echo "0")
                if [ "$SIZE" -gt 24 ]; then  # pcap header is 24 bytes
                    SIZE_H=$(ls -lh "./$FILENAME" | awk '{print $5}')
                    echo "Capture saved to: $FILENAME (Size: $SIZE_H)"
                    echo ""
                    echo "Open in Wireshark with: wireshark $FILENAME"
                else
                    echo "Warning: Capture file is empty. No packets captured with filter: $FILTER"
                    echo "Try capturing all traffic with: ./docker-run.sh capture $ROUTER \"\""
                    rm -f "./$FILENAME"
                fi
            else
                echo "Warning: Could not retrieve capture file."
            fi
        }

        # Set trap for Ctrl+C
        trap cleanup_and_copy INT TERM

        # Start tcpdump in the container with unbuffered writes (-U)
        docker exec "$CONTAINER" tcpdump -U -i any $FILTER -w /app/logs/$FILENAME 2>&1

        # If we reach here without Ctrl+C, cleanup anyway
        cleanup_and_copy
        ;;

    help|*)
        cat <<EOF
RIPv2 Docker Quick Start Script

Usage: ./docker-run.sh [command] [options]

Commands:
    build                Build Docker images for all routers
    start                Start all routers in background (detached mode)
    start-fg             Start all routers in foreground (see logs directly)
    stop                 Stop all routers and remove containers
    restart              Restart all routers
    logs [router]        Follow logs (all routers or specific router, e.g., r1)
    status               Show status of all router containers
    shell [router]       Open a shell in a router container (default: r1)
    cli [router]         Attach to router CLI (default: r1)
    capture [router] [filter]  Capture packets from router (Ctrl+C to stop)
    clean                Remove all containers, networks, and images
    rebuild              Clean rebuild (no cache) and restart
    test                 Run basic connectivity tests
    help                 Show this help message

Examples:
    ./scripts/docker-run.sh build                    # Build images
    ./scripts/docker-run.sh start                    # Start all routers
    ./scripts/docker-run.sh logs r1                  # View logs from router R1
    ./scripts/docker-run.sh shell r3                 # Open shell in router R3
    ./scripts/docker-run.sh capture r1               # Capture RIP traffic on R1 (Ctrl+C to stop)
    ./scripts/docker-run.sh capture r2 "icmp"        # Capture ICMP on R2
    ./scripts/docker-run.sh capture r3 "port 520"    # Capture RIP on R3
    ./scripts/docker-run.sh test                     # Test the setup

For more information, see docs/README.md
EOF
        ;;
esac
