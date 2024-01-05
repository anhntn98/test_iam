import re
import logging


logger = logging.getLogger('pms')

class OperaRecord(object):
    type = None
    datas = []
    def __init__(self, message):
        datas = str(message).split('|')
        if len(datas) > 1:
            self.datas = datas[1:]
            if len(datas[0]) == 2:
                self.type = datas[0]
                if self.type == 'GC':
                    if re.search(r'GC\|(.*)\|RN(\d+)\|(.*)\|RO(\d+)\|.*', message):
                        # Guest move to another room
                        self.type = 'GM' # Guest Move
        else:
            logger.debug(f'Invalid PMS message: {message}')

    def is_valid(self):
        """Check if the message is has valid format or required fields"""
        match self.type:
            case 'DS':
                return True
            case 'DE':
                return True
            case 'GI':
                """Guest check in"""
                return all([self.RN, self.GID, self.GN])
            case 'GC':
                """Guest change"""
                return all([self.RN, self.GID])
            case 'GO':
                """Guest check out"""
                return all([self.RN])
            case 'GM':
                """Guest move to another room"""
                return all([self.GID, self.RN, self.RO])
            case _:
                """Unknown message type"""
                return False
    
    @property
    def RN(self):
        """RN: Room Number - ANS, max. 8 (can be longer with Suite8 or OPERA-PMS)"""
        a = list(filter(lambda e: 'RN' in e, self.datas))
        return a[0].removeprefix('RN') if a else None
    @property
    def GN(self)->str:
        """GN: Guest Name - ANS, max. 200"""
        a = list(filter(lambda e: 'GN' in e, self.datas))
        return a[0].removeprefix('GN') if a else None
    @property
    def GID(self)->int:
        """G#: Reservation Number - N, max. 10"""
        a = list(filter(lambda e: 'G#' in e, self.datas))
        return int(a[0].removeprefix('G#')) if a else None
    @property
    def GV(self)->str:
        """GV: Guest VIP Status - AN, max. 20 (normally numeric values)"""
        a = list(filter(lambda e: 'GV' in e, self.datas))
        return a[0].removeprefix('GV') if a else None
    @property
    def GT(self)->str:
        """GT: Guest Title - ANS, max. 20"""
        a = list(filter(lambda e: 'GT' in e, self.datas))
        return a[0].removeprefix('GT') if a else None
    @property
    def GA(self):
        """Guest Arrival Date - D"""
        a = list(filter(lambda e: 'GA' in e, self.datas))
        return a[0].removeprefix('GA') if a else None
    @property
    def GD(self):
        """Guest Departure Date - D"""
        a = list(filter(lambda e: 'GD' in e, self.datas))
        return a[0].removeprefix('GD') if a else None
    @property
    def GL(self):
        """Guest Language - ANS, max. 10"""
        a = list(filter(lambda e: 'GL' in e, self.datas))
        return a[0].removeprefix('GL') if a else None
    # @property
    # def GS(self)-> bool:
    #     """GS: Share Flag - AN, 1 char (Y/N)"""
    #     a = list(filter(lambda e: 'GS' in e, self.datas))
    #     if a:
    #         flag = a[0].removeprefix('GS')
    #         return True if flag == 'Y' else False
    #     return None
    @property
    def RO(self):
        """RO: Old Room Number (source room) - ANS, max. 8 (can be longer with Suite8 or OPERA-PMS)"""
        a = list(filter(lambda e: 'RO' in e, self.datas))
        return a[0].removeprefix('RO') if a else None




# ms = "GI|RN1003|GSY|G#12329|"
# c = Opera_Record(ms)
# if not c.is_valid():
#     raise Exception('Invalid message')
# # if message is valid, then do something
# match c.type:
#     case 'GI': pass #do something
#     case 'GO': pass #do something
#     case 'GC': pass #do something