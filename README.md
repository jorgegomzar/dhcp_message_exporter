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
