import logging
from dhcp_message_exporter.monitor import start_exporter


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_exporter()
