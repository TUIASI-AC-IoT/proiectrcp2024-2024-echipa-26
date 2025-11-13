#!/bin/bash


set -e

echo "=========================================="
echo "Starting RIPv2 Router - ID: $ID"
echo "=========================================="

CFG_DIR="/app/cfg/r${ID}"

if [ ! -d "$CFG_DIR" ]; then
    echo "ERROR: Configuration directory $CFG_DIR not found!"
    exit 1
fi

echo "Configuring network interfaces..."

for config_file in "$CFG_DIR"/*.conf; do
    if [ -f "$config_file" ]; then
        echo "Processing: $config_file"

        interface=$(grep "^interface=" "$config_file" | cut -d'=' -f2)
        ip_addr=$(grep "^ip=" "$config_file" | cut -d'=' -f2)
        subnet=$(grep "^subnet=" "$config_file" | cut -d'=' -f2)

        echo "  Interface: $interface"
        echo "  IP: $ip_addr"
        echo "  Subnet: $subnet"

        ip addr show | grep -q "$ip_addr" && echo "  ✓ IP $ip_addr is configured" || echo "  ⚠ IP $ip_addr not found (Docker should handle this)"
    fi
done

echo ""
echo "Network configuration complete."
echo ""

echo "Current network interfaces:"
ip addr show

echo ""
echo "Current routing table:"
ip route show

echo ""
echo "=========================================="
echo "Starting RIPv2 Router Application"
echo "=========================================="

exec python3 /app/main.py
