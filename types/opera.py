import socket
import logging
from typing import TypedDict
from django.utils import timezone

from .base import PMS

logger = logging.getLogger(__name__)

class OperaPMS(PMS):
    """OPERA PMS class"""
    def __init__(self, host: str, port: int, username: str, password: str, timeout: int = 10):
        super().__init__(host, port, username, password, timeout)
        # self._login()

    
    def get_date():
        """
        It returns a string that starts with `DA` and ends with the current date in the format `YYMMDD`
        :return: The date in the format of DAyymmdd
        """
        return 'DA{}'.format(timezone.now().strftime('%y%m%d'))
    
    def time_format():
        return 'TI'.format(timezone.now().strftime('%H%M%S'))
    
    def get_datetime(self):
        return '{}|{}'.format(self.get_date(), self.time_format())
    
    def record(self, message):
        return str(b'\x02' + message.encode() + b'\x03')
    
    @property
    def link_start(self):
        # LS|DA120215|TI123045|
        return self.record('LS|' + self.get_datetime() + '|\n')
    
    @property
    def link_end(self):
        # LE|DA170825|TI044245|..LE|DA170825|TI114004|.
        return self.record('LE|' + self.get_datetime() + '|')
    
    @property
    def link_description(self):
        # LD|DA120215|TI123046|V#1.01|IFWW|
        return self.record('LD|' + self.get_datetime() + '|V#1.01|IFWW|\n')
    
    @property
    def link_alive(self):
        # LA|DA120215|TI112350|
        return self.record('LA|' + self.get_datetime() + '|')
    
    def start_connection(self):
        """
        It sends three messages to the PMS to start connection, and if any of them fail, it returns False
        """
        try:
            self.sock.send(self.link_start)
            self.sock.settimeout(3)
        except socket.error:
            logger.error('PMS_CLIENT: Fail to send link start message to pms server {}'.format(self.host))
            return False
        else:
            logger.debug('PMS_CLIENT: Success to send link start message to pms server {}'.format(self.host))
            
        try:
            self.sock.send(self.link_description)
            self.sock.settimeout(3)
        except socket.error:
            logger.error('PMS_CLIENT: Fail to send link description message to pms server {}'.format(self.host))
            return False
        else:
            logger.debug('PMS_CLIENT: Success to send link description message to pms server {}'.format(self.host))

        try:
            self.sock.send(self.link_alive)
            self.sock.settimeout(3)
        except socket.error:
            logger.error('PMS_CLIENT: Fail to send link alive message to pms server {}'.format(self.host))
            return False
        else:
            logger.debug('PMS_CLIENT: Success to send link alive message to pms server {}'.format(self.host))
            
    def _close(self):
        """
        _close() closes the connection to the PMS
        """
        self.sock.close()
        self.connected = False
        logger.debug('PMS_CLIENT: Close connection')

