import os
import logging
from enum import Enum
from prometheus_client import start_http_server, Counter
from scapy.all import sniff
from scapy.layers.dhcp import DHCP
from scapy.layers.l2 import Ether
from typing import Optional, Type, TypeVar

logger = logging.getLogger("dhcp_message_exporter")

# Prometheus counters
dhcp_discover_counter = Counter('dhcp_discover_total', 'Total number of DHCP Discover messages')
dhcp_offer_counter = Counter('dhcp_offer_total', 'Total number of DHCP Offer messages')
dhcp_request_counter = Counter('dhcp_request_total', 'Total number of DHCP Request messages')
dhcp_ack_counter = Counter('dhcp_ack_total', 'Total number of DHCP Acknowledge messages')
dhcp_nak_counter = Counter('dhcp_nak_total', 'Total number of DHCP NAK messages')
dhcp_message_counter = Counter('dhcp_message_total', 'Total number of DHCP messages', ['message_type', 'source_mac', 'destination_mac'])


DEFAULT_DHCP_MESSAGE_EXPORTER_PORT = 8000

T = TypeVar("T", bound="DHCPMessageType")


class DHCPMessageType(Enum):
    def __init__(self, prometheus_counter: Counter, type_int: int) -> None:
        super().__init__()
        self.prometheus_counter = prometheus_counter
        self.type_int = type_int

    @classmethod
    def get_by_type_int(cls: Type[T], type_int: Optional[int]) -> Optional[T]:
        if not type_int:
            return None

        for item in cls:
            if item.type_int == type_int:
                return item
        return None

    DISCOVER = (dhcp_discover_counter, 1)
    OFFER = (dhcp_offer_counter, 2)
    REQUEST = (dhcp_request_counter, 3)
    ACK = (dhcp_ack_counter, 5)
    NAK = (dhcp_nak_counter, 6)


def handle_dhcp_packet(packet):
    if DHCP not in packet:
        return

    src_mac = packet[Ether].src
    dst_mac = packet[Ether].dst
    dhcp_options = packet[DHCP].options

    dhcp_type: Optional[int] = next((
        opt[1]
        for opt in dhcp_options
        if opt[0] == 'message-type'
    ), None)

    if not (dhcp_type_enum := DHCPMessageType.get_by_type_int(dhcp_type)):
        return

    dhcp_type_enum.prometheus_counter.inc()
    dhcp_message_counter.labels(
        message_type=dhcp_type_enum.name,
        source_mac=src_mac,
        destination_mac=dst_mac,
    ).inc()

    logger.info(f"{dhcp_type_enum.name} [{src_mac} -> {dst_mac}] registered")


def start_exporter():
    start_http_server(int(os.getenv("DHCP_MESSAGE_EXPORTER_PORT", DEFAULT_DHCP_MESSAGE_EXPORTER_PORT)))

    logger.info("Exporter ready!")

    sniff(filter="udp port 67 or udp port 68", prn=handle_dhcp_packet, store=0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_exporter()
