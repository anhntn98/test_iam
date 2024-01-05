import socket
import logging
from typing import TypedDict
from django.utils import timezone


logger = logging.getLogger(__name__)

class PMS_Config(TypedDict):
    host: str
    port: int
    username: str
    password: str
    timeout: int

class PMS():
    """PMS class"""
    host: str
    port: int
    username: str
    password: str
    timeout: int = 10
    sock = None
    connected = False
    
    def __init__(self, config: PMS_Config):
        self._connect()

    def _connect(self):
        """
        It creates a socket, sets the timeout, creates a list of the socket, and then connects to the
        PMS with host and port
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.inout = [self.sock]
        self.sock.connect((self.host, self.port))
        self.connected = True

