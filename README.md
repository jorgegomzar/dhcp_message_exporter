# DHCP message exporter for Prometheus

This is a Python app that will sniff all DHCP traffic and serve an API for Prometheus to import data.

## Configuration

You can change the port the exporter uses by defining this env variable `DHCP_MESSAGE_EXPORTER_PORT`.
By default the exporter will try to listen port `8000`.

You might need to set your network interface in promiscuous mode to be able to properly use the `dhcp_offer_per_server_count` metric 
as an alarm for Rogue DHCP servers.

## Usage

```
# install dependencies
poetry install

# run
python main.py
```

### Docker usage

```
docker build . -t dhcp_message_exporter
# or docker build https://github.com/jorgegomzar/dhcp-message-exporter.git#main

# has some issues in MacOS
docker run --restart=unless-stopped --network=host dhcp_message_exporter
```

Then, add the endpoint to your Prometheus configuration file:

```
scrape_configs:
  - job_name: dhcp_messages
    static_configs:
      - targets: ['localhost:8000']  # or the port of your choice
```

And in your rules, you can set an alert for rogue DHCP servers like this (replace `authorized_dhcp_ip1`, and `authorized_dhcp_ip2` with your known DHCP servers):
```
groups:
  - name: DHCPAlerts
    rules:
    - alert: RogueDHCPServerDetected
      expr: dhcp_offer_per_server_count > 0 and ignoring(server_ip) dhcp_offer_per_server_count unless (server_ip in ["authorized_dhcp_ip1", "authorized_dhcp_ip2"])
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Rogue DHCP Server Detected"
        description: "A rogue DHCP server with IP {{ $labels.server_ip }} is detected on the network."
```
